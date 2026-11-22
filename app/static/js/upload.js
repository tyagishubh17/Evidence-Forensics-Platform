// Client-side interactions for file upload and cryptographic hash copying.
(function () {
  var ALLOWED = ["pdf", "doc", "docx", "jpg", "jpeg", "png", "txt"];
  var MAX_BYTES = 16 * 1024 * 1024;

  function formatSize(bytes) {
    if (bytes < 1024) return bytes + " bytes";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(2) + " MB";
  }

  function extensionOf(name) {
    var dot = name.lastIndexOf(".");
    return dot === -1 ? "" : name.slice(dot + 1).toLowerCase();
  }

  // Upload preview feedback
  var input = document.getElementById("evidence-file");
  var dropZone = document.getElementById("drop-zone");

  function showSelectedFile() {
    var box = document.getElementById("selected-file");
    var warning = document.getElementById("selected-warning");
    if (!input || !box) return;

    var file = input.files[0];
    if (!file) { box.hidden = true; return; }

    var ext = extensionOf(file.name);
    var nameEl = document.getElementById("selected-name");
    var sizeEl = document.getElementById("selected-size");
    var typeEl = document.getElementById("selected-type");

    if (nameEl) nameEl.textContent = file.name;
    if (sizeEl) sizeEl.textContent = formatSize(file.size);
    if (typeEl) typeEl.textContent = (file.type || "unknown type") + (ext ? " (." + ext + ")" : "");

    var message = "";
    if (ALLOWED.indexOf(ext) === -1) {
      message = "This file type is not allowed. Allowed: PDF, DOC, DOCX, JPG, JPEG, PNG, TXT.";
    } else if (file.size === 0) {
      message = "This file is empty (0 bytes).";
    } else if (file.size > MAX_BYTES) {
      message = "This file is larger than 16 MB.";
    }

    if (warning) {
      warning.textContent = message;
      warning.hidden = message === "";
    }
    box.hidden = false;
  }

  if (input && dropZone) {
    input.addEventListener("change", showSelectedFile);

    ["dragenter", "dragover"].forEach(function (name) {
      dropZone.addEventListener(name, function (event) {
        event.preventDefault();
        dropZone.classList.add("is-dragover");
      });
    });

    ["dragleave", "drop"].forEach(function (name) {
      dropZone.addEventListener(name, function () {
        dropZone.classList.remove("is-dragover");
      });
    });

    dropZone.addEventListener("drop", function (event) {
      event.preventDefault();
      if (event.dataTransfer.files.length) {
        input.files = event.dataTransfer.files;
        showSelectedFile();
      }
    });
  }

  // Copy-to-clipboard handler with fallback
  document.querySelectorAll("[data-copy-target]").forEach(function (button) {
    button.addEventListener("click", function () {
      var targetId = button.getAttribute("data-copy-target");
      var el = document.getElementById(targetId);
      if (!el) return;
      var text = el.textContent.trim();

      function showCopied() {
        var originalHtml = button.innerHTML;
        button.innerHTML = "<span>✓ Copied!</span>";
        button.classList.add("btn-success");
        setTimeout(function () {
          button.innerHTML = originalHtml;
          button.classList.remove("btn-success");
        }, 1800);
      }

      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(showCopied).catch(function () {
          fallbackCopy(text);
        });
      } else {
        fallbackCopy(text);
      }

      function fallbackCopy(val) {
        var temp = document.createElement("textarea");
        temp.value = val;
        document.body.appendChild(temp);
        temp.select();
        try {
          document.execCommand("copy");
          showCopied();
        } catch (e) {
          console.error("Unable to copy", e);
        }
        document.body.removeChild(temp);
      }
    });
  });
})();
