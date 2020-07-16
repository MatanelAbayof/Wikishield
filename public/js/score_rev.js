
window.addEventListener("DOMContentLoaded", (event) => {
    const dom = new DomManager();

    dom.revIn.addEventListener("input", () => dom.hideErrMsg());

    dom.checkRevBt.addEventListener("click", () => {
        dom.checkRevBt.disabled = true;
        dom.scoreRes.innerText = "";

        let revText = dom.revIn.value.trim();

        // TODO: show progress bar while fetch and disable input and button. for test, use wait(2000) Promise.

        validInput(revText)
        .then(() => WikishieldApi.getScoreRev(getLang(), revText))
        .then(scoreResult => {
                let badScore = scoreResult[0];
                dom.scoreRes.innerText = badScore.toFixed(3);
                dom.checkRevBt.disabled = false;
        })
        .catch(errMsg => {
            dom.errMsgInput.textContent = errMsg;
            DomManager.showElement(dom.errMsgInput);
            dom.checkRevBt.disabled = false;
            //dom.showErrDialog(errMsg);
        });
    });

    /** validate input: */
    function validInput(revText){
        return new Promise((resolve, reject) => (revText.trim() === "") ? reject("Please enter an input!") : resolve());
    }

    }
);


//--------------------------------------------------------------------------------------------------------------------
/** DOM manager class */
class DomManager extends BaseDomManager {

    constructor() {
        super();
        this.revIn = document.getElementById("rev-text");
        this.checkRevBt = document.getElementById("check-rev-bt");
        this.scoreRes = document.getElementById("score-result");
        this.errMsgInput = document.querySelector("#rev-text + small");
    }

    /** hide error message: */
    hideErrMsg() {
        DomManager.hideElement(this.errMsgInput);
    }
}



