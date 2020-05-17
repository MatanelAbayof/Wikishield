let chooseLangControl = null;

window.addEventListener("DOMContentLoaded", () => {
    console.log("toolbar load");
    chooseLangControl = document.getElementById("choose-lang");
    chooseLangControl.value = getLang();

    const changeLangEvent = new Event('changeLang');

    chooseLangControl.addEventListener('changeLang', function () { 
        //console.log("lang changed");
    });

    chooseLangControl.addEventListener("change", () => {
        let lang = chooseLangControl.value;
        setLang(lang);
        // call listeners to lang change
        chooseLangControl.dispatchEvent(changeLangEvent);
    });
});

/** get language */
function getLang() {
    let lang = $.cookie("lang");
    if(lang == null)
        lang = "en";
    return lang;
}

/** set language */
function setLang(lang) {
    $.cookie("lang", lang);
}