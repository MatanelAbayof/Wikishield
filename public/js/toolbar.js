let chooseLangControl = null;

window.addEventListener("DOMContentLoaded", () => {

    chooseLangControl = document.getElementById("choose-lang");
    chooseLangControl.value = getLang();

     fetch("langs.json")
    .then(response => response.json())
    .then(data => chooseLangControl.innerHTML = buildLangOptions(data.langs));

    const changeLangEvent = new Event('changeLang');

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

function buildLangOptions(langs){
    let options = '';
    for(var i = 0; i < langs.length; i++){
        options += "<option value=" + langs[i].name + ">" + langs[i].language + "</option>";
    }
    return options;
}