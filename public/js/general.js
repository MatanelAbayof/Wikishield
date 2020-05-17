/** base DOM manager class */
class BaseDomManager {

    constructor() {
        if (new.target === BaseDomManager)
            throw new TypeError("Cannot construct Abstract instances directly");
        this.$errMsgModal = $("#err-msg-modal");
        this.errMsgModalBody = document.querySelector("#err-msg-modal .modal-body");
    }

    /** remove item from array */
    static removeArrItem(arr, item) {
        let indexItem = arr.indexOf(item);
        if (indexItem > -1)
            arr.splice(indexItem, 1);
    }

    /** show element */
    static showElement(element) {
        element.style.display = "block";
    }

    /** hide element */
    static hideElement(element) {
        element.style.display = "none";
    }

    /** toggle element */
    static toggleElement(element) {
        element.style.display = (getComputedStyle(element, null).display === "none") ? "block" : "none";
    }

    /** toggle elements */
    static toggleElements(elements) {
        elements.forEach((element) => { BaseDomManager.toggleElement(element); });
    }

    /** show error dialog */
    showErrDialog(msg) {
        this.errMsgModalBody.textContent = msg;
        this.$errMsgModal.modal("show");
    }
}

//--------------------------------------------------------------------------------------------------------------------
/** base API class */
class BaseApi {

    /** get API URL */
    static get apiUrl() {
        throw "Not implemented method!"; // this is a pure virtual method
    }

    /**
     * fetch JSON from server
     * @param relativePath - relative path in our server
     * @param methodType - method type. e.g. POST
     * @param bodyData - body data
     * @returns Promise of fetch JSON result
     */
    static fetchJSON(relativePath, methodType = "GET", bodyData = null) {
        let absolutePath = encodeURI(`${this.apiUrl}/${relativePath}`);

        let body = (bodyData == null) ? null : JSON.stringify(bodyData);
        const options = {
            method: methodType,
            body: body,
            headers: {
              'Content-Type': 'application/json'
            }
        };

        let status = null;
        return fetch(absolutePath, options)
            .then(response => {
                status = response.status;
                return response.json();
            })
            .then(allData => {
                if(status !== 200)
                    throw allData.errInfo.errMsg; // throw an error message
                return allData.data;
            });
    }
}

//--------------------------------------------------------------------------------------------------------------------
/** Wikishield API class */
class WikishieldApi extends BaseApi {

    /** API URL */
    static get apiUrl() {
        return "/api";
    }

    /** request score revision text */
    static getScoreRev(lang, revText) {
        let params = new URLSearchParams();
        params.append("lang", lang);
        params.append("rev_text", revText);
        let reqUrl = `score_rev?${params.toString()}`;
        return this.fetchJSON(reqUrl)
               .then(data => data.scoreResult);
    }

    /** get recent unverified revisions */
    static getRecentUnverifiedRevs(lang, numRevs) {
        let params = new URLSearchParams();
        params.append("lang", lang);
        params.append("num_revs", numRevs);
        let reqUrl = `get_revs?${params.toString()}`;
        return this.fetchJSON(reqUrl)
               .then(data => data.revs);
    }

    /** manage revision */
    static manageRev(lang, revId, goodEditing) {
        let reqUrl = "manage_rev";
        let bodyData = {
            lang: lang,
            rev_id: revId,
            good_editing: goodEditing
        };
        return this.fetchJSON(reqUrl, "POST", bodyData);
    }

}