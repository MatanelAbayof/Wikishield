window.addEventListener("DOMContentLoaded", () => {
    const dom = new DomManager();

    const numRevs = 50;
    let revs = [];

    loadRevs();

    // listen to change lang event
    chooseLangControl.addEventListener('changeLang', function () { 
        loadRevs();
    });


    /** load revisions */
    function loadRevs() {
        // clean last revisions
        dom.clearRevsTbl();
        DomManager.hideElement(dom.verifyTbl);
        DomManager.hideElement(dom.infoMsg);
        dom.showRefreshIcon();

        WikishieldApi.getRecentUnverifiedRevs(getLang(), numRevs)
        .then(fetchRevs => {
            revs = fetchRevs;

            dom.hideRefreshIcon();
            // check if not found revisions and show info message
            if(revs.length === 0) {
                dom.showInfoMsg(DomManager.NOT_FOUND_REVS_INF_MSG);
            } else {
                dom.fillRevsTbl(revs);
            }

            // handle verify buttons
            dom.verifyBts.forEach((bt, _) => {
                bt.addEventListener("click", () => {
                    const row = bt.parentNode.parentNode;
                    let idx = dom.findRowIdx(row);
                    let rev = revs[idx];

                    dom.listenConfirmVerifyBtClick(() => manageRev(idx, rev, 1)); // 1 for verify
                    dom.showConfirmVerifyDialog();
                });
            });

            // handle restore buttons
            dom.restoreBts.forEach((bt, _) => {
                bt.addEventListener("click", () => {
                    const row = bt.parentNode.parentNode;
                    let idx = dom.findRowIdx(row);
                    let rev = revs[idx];

                    dom.listenConfirmRestoreBtClick(() => manageRev(idx, rev, 0)); // 0 for restore
                    dom.showConfirmRestoreDialog();
                });
            });


        }).catch(errMsg => {
            console.error(errMsg);
            dom.showErrDialog(errMsg);
        });
    }


    /** manage a revision 
     * param goodEditing to note if verify or restore */
    function manageRev(idx, rev, goodEditing) {
        // call manage revision at API
        let revId = rev.id;
        WikishieldApi.manageRev(getLang(), revId, goodEditing)
        .then(_ => {
            dom.delRow(idx);
            revs.splice(idx, 1); // remove revision from array

            // check if not found revisions and show info message
            if(revs.length === 0) {
                dom.showInfoMsg(DomManager.NOT_FOUND_REVS_INF_MSG);
            }
        }).catch(errMsg => {
            console.error(errMsg);
            dom.showErrDialog(errMsg);
        });
    }

});

//--------------------------------------------------------------------------------------------------------------------
/** DOM manager class */
class DomManager extends BaseDomManager {

    constructor() {
        super();
        this.verifyTbl = document.getElementById("verify-tbl");
        this.verifyTblBody = this.verifyTbl.querySelector("tbody");
        this.verifyBts = [];
        this.restoreBts = [];
        this.infoMsg = document.getElementById("info-msg");
        this.verifyModal = document.getElementById("confirm-verify");
        //this.verifyModalBt = this.verifyModal.querySelector("button.bt-verify");
        this.restoreModal = document.getElementById("confirm-restore");
        //this.restoreModalBt = this.restoreModal.querySelector("button.bt-restore");
        this.$confirmVerify = $("#confirm-verify");
        this.$confirmVerifyBt = $("button.bt-verify", this.$confirmVerify);
        this.$confirmRestore = $("#confirm-restore");
        this.$confirmRestoreBt = $("button.bt-restore", this.$confirmRestore);
        this.refreshIcon = document.getElementById("refresh-icon");
    }

    /** show info message */
    showInfoMsg(msg) {
        this.infoMsg.innerHTML = msg;
        DomManager.hideElement(this.verifyTbl);
        DomManager.showElement(this.infoMsg);
    }

    /** fill revisions in table */
    fillRevsTbl(revs) {
        revs.forEach((rev, idx) => this.addRevRow(idx, rev));
        this.verifyBts = this.verifyTbl.querySelectorAll("button.verify-bt");
        this.restoreBts = this.verifyTbl.querySelectorAll("button.restore-bt");

        DomManager.hideElement(this.infoMsg);
        DomManager.showElement(this.verifyTbl);
    }

    /** update rows indices at table */
    updateRowsIndices() {
        const rowsIndices = this.verifyTblBody.querySelectorAll("tr th:first-child");
        rowsIndices.forEach((rowIdx, idx) => {
            rowIdx.innerHTML = (idx + 1).toString();
        });
    }

    /** find row index at table */
    findRowIdx(row) {
        return Array.from(row.parentNode.children).indexOf(row);
    }

    /** delete row at table */
    delRow(idx) {
        const rowNode = this.verifyTblBody.querySelector(`tr:nth-child(${idx+1})`);
        this.verifyTblBody.removeChild(rowNode);
        this.updateRowsIndices();
    }

    /** clear revisions table */
    clearRevsTbl() {
        this.verifyTblBody.innerHTML = "";
    }

    /** add a revision row to table */
    addRevRow(idx, rev) {
        let rowNum = idx + 1;
        let pageTitle = (rev.page_title == null) ? "" : rev.page_title;
        let lang = getLang();
        let pageLink = encodeURI(`https://${lang}.wikipedia.org/wiki/${pageTitle}`);
        let compareLink = encodeURI(`https://${lang}.wikipedia.org/w/index.php?title=${pageTitle}&type=revision&diff=${rev.wiki_id}&oldid=${rev.parent_id}`);
        let revDate = moment.utc(rev.timestamp, "YYYY-MM-DD HH:mm:ss.S").fromNow();

        
        let revScore = (rev.score != null) ? rev.score.toFixed(2) : 1;

        let rowTbl = `<tr>
                        <th scope="row">${rowNum}</th>
                        <td><a href="${pageLink}" target="_blank">${pageTitle}</a></td>
                        <td><a href="${compareLink}" target="_blank">Compare link</a></td>
                        <td>${revDate}</td>
                        <td class="limited-text" data-toggle="tooltip" data-placement="top" title="${rev.content}">${rev.content}</td>
                        <td >${revScore}</td>
                        <td>
                            <button type="button" class="btn btn-success verify-bt">No</button>
                            <button type="button" class="btn btn-danger restore-bt">Yes</button>
                        </td>
                      </tr>`;

        this.verifyTblBody.innerHTML += rowTbl;
    }

    /** show confirm verify dialog */
    showConfirmVerifyDialog() {
        this.$confirmVerify.modal("show");
    }

    /** show confirm restore dialog */
    showConfirmRestoreDialog() {
        this.$confirmRestore.modal("show");
    }

    /**
     * listen to confirm verify button event.
     * all last event listeners will removed
     */
    listenConfirmVerifyBtClick(onClick) {
        this.$confirmVerifyBt.unbind();
        this.$confirmVerifyBt.click((e) => onClick());
    }

    /**
     * listen to confirm restore button event.
     * all last event listeners will removed
     */
    listenConfirmRestoreBtClick(onClick) {
        this.$confirmRestoreBt.unbind();
        this.$confirmRestoreBt.click((e) => onClick());
    }

    showRefreshIcon() {
        DomManager.showElement(this.refreshIcon);
    }

    hideRefreshIcon() {
        this.refreshIcon.setAttribute('style', 'display: none !important');
    }
}

DomManager.NOT_FOUND_REVS_INF_MSG = "Not found revisions to display!";