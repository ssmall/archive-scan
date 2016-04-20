'use strict';

var BUCKET = "archive.smallfami.ly";
var KEY_PREFIX = "scans/";


// Initialize the Amazon Cognito credentials provider
AWS.config.region = 'us-east-1'; // Region
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:2dba5bdf-90b6-4f03-8eac-eb85ded10fda'
});

AWS.config.credentials.get();

var s3 = new AWS.S3({'region': 'us-west-1'});

function S3UploadDeferred(params, options) {
    var deferred = $.Deferred();
    var request = null;
    if (options) {
        request = s3.upload(params, options);
    } else {
        request = s3.upload(params);
    }
    request.on('httpUploadProgress', function (progress) {
            deferred.notify(false, progress);
        })
        .on('retry', function (response) {
            deferred.notify(response.error);
        })
        .send(function (err, data) {
            if (err) {
                deferred.reject(err);
            } else {
                deferred.resolve(data);
            }
        });
    return deferred;
}

function checkIfFileExists(key) {
    var params = {
        Bucket: BUCKET,
        Key: KEY_PREFIX + key
    };
    var deferred = $.Deferred();
    s3.headObject(params, function (err, data) {
        if (err) {
            deferred.reject(err);
        } else {
            deferred.resolve(data);
        }
    });
    return deferred;
}

function uploadImageToS3(folder, key, image) {
    var params = {
        Bucket: BUCKET,
        Key: KEY_PREFIX + folder + "/" + key,
        Body: image
    };
    if (image.type) {
        params['ContentType'] = image.type;
    }
    return new S3UploadDeferred(params);
}

function uploadIndexEntryToS3(imageKey, text, keywords) {
    var entry = {
        'imageKey': imageKey
    };
    if (text) {
        entry['text'] = text;
    }
    if (keywords) {
        entry['keywords'] = keywords;
    }
    var fileKey = splitExt(imageKey).name + ".json";

    var params = {
        Bucket: BUCKET,
        Key: fileKey,
        Body: JSON.stringify(entry),
        ContentType: 'application/json; charset=utf-8'
    };

    return new S3UploadDeferred(params);
}


function splitExt(filename) {
    var basename = filename.substring(0, filename.lastIndexOf("."));
    var extension = filename.substring(filename.lastIndexOf(".") + 1)
    return {
        'name': basename,
        'ext': extension
    };
}

function validateRequiredInputs() {
    var validated = true;
    $("input[required]").each(function (idx, item) {
        var $item = $(item);
        if (!$item.val()) {
            validated = false;
            $item.addClass('error');
        }
    });
    return validated;
}

$(function () {
    var $albumTitleInput = $("input#albumTitle");
    var $albumPageNumberInput = $("input#albumPageNumber");
    var $imageFileInput = $("input#imageFile");
    var $loadedImg = $("#loadedImage");
    var $imageTextInput = $("input#imageText");
    var $textEntry = $("textarea#textEntry");
    var $saveTextLink = $("a#saveText");
    var $keywordsContainer = $("#keywordsContainer");
    var $keywordsInput = $("textarea#keywords");
    var $uploadProgress = $("#uploadProgress");
    var $reloadPageLink = $("a#reloadPageLink");

    var urlParams = $.url('?');
    if (urlParams) {
        if (urlParams.title) {
            $albumTitleInput.val(urlParams.title);
        }
        if (urlParams.page) {
            $albumPageNumberInput.val(urlParams.page);
        }
    }

    window.selectImage = function (evt) {
        $loadedImg.attr('src', URL.createObjectURL(evt.target.files[0]));
        $loadedImg.removeClass('hidden');
    };

    window.selectText = function (evt) {
        $textEntry.removeClass('hidden');
        var reader = new FileReader();
        var deferredResult = $.Deferred();
        reader.onload = deferredResult.resolve;
        var file = evt.target.files[0];
        reader.readAsText(file);

        deferredResult.then(function (event) {
            var resultText = event.target.result;
            var processedText = resultText.split(/\n+/)
                .filter(function (str) {
                    return str.search(/^\s*$/) === -1;
                })
                .map(function (s) {
                    return s.trim();
                })
                .join(" ");
            $textEntry.val(processedText);
            $saveTextLink.removeClass('hidden');
            var nameAndExtension = splitExt(file.name);
            $saveTextLink.attr('download', nameAndExtension.name + "_modified." + nameAndExtension.ext);
        });
    };

    window.saveButtonClicked = function (evt) {
        $textEntry.attr('readonly', 'readonly');
        $imageTextInput.attr('disabled', 'disabled');
        $saveTextLink.remove();
        $keywordsContainer.removeClass('hidden');
    };

    window.textChanged = function (evt) {
        var textToSave = $(evt.target).val();
        var textFileAsBlob = new Blob([textToSave], {type: 'text/plain; charset=utf-8'});
        $saveTextLink.attr('href', URL.createObjectURL(textFileAsBlob));
    };

    window.uploadEntry = function (evt) {
        if (!validateRequiredInputs()) {
            console.warn("Cannot upload without all required fields!");
            return;
        }
        var image = $imageFileInput[0].files[0];
        var imageExt = splitExt(image.name).ext;
        var albumTitle = $albumTitleInput.val();
        var folder = albumTitle.replace(/\s/, "_");
        var pageNum = $albumPageNumberInput.val();
        var baseFileName = "page" + pageNum;
        var imageFileName = baseFileName + "." + imageExt;

        var imageText = $textEntry.val();
        var imageKeywords = $keywordsInput.val();
        if (imageKeywords) {
            imageKeywords = imageKeywords.split(/\n/).filter(function (el) {
                return el;
            });
        }

        var retries = 0;

        var shouldContinue = $.Deferred();
        checkIfFileExists(folder + "/" + baseFileName + ".json")
            .then(function () {
                    var ok = confirm("Page " + pageNum + " already exists! Overwrite it?");
                    if (ok) {
                        shouldContinue.resolve();
                    } else {
                        shouldContinue.reject();
                    }
                },
                shouldContinue.resolve);
        shouldContinue.done(function () {
            uploadImageToS3(folder, imageFileName, image)
                .then(function (data) {
                        console.info("Successfully uploaded image to '" + data.Bucket + "/" + data.Key + "'");
                        $uploadProgress.text("Done!");
                        return uploadIndexEntryToS3(data.Key, imageText, imageKeywords);
                    },
                    function (err) {
                        console.error(err);
                    },
                    function (retryError, progress) {
                        if (retryError) {
                            console.warn("Retrying after error: " + retryError);
                            retries++;
                        }
                        $uploadProgress.removeClass('hidden');
                        var progressText = Math.floor(100 * progress.loaded / progress.total) + "%";
                        if (retries) {
                            progressText = progressText + " (retry " + retries + ")";
                        }
                        $uploadProgress.text(progressText);
                    })
                .then(function (data) {
                        console.info("Successfully uploaded index entry to '" + data.Bucket + "/" + data.Key + "'");
                        $(evt.target).remove();
                        $reloadPageLink.attr('href', "?" + $.param({
                                'page': parseInt(pageNum) + 1,
                                'title': albumTitle
                            }));
                        $reloadPageLink.removeClass('hidden');
                    },
                    function (err) {
                        console.error(err);
                    });
        });
    };
});