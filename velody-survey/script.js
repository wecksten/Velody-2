
const questionE1 = document.getElementById('quiz');
const submitBtn = document.getElementById('submit');
const answerEls = document.querySelectorAll(".answer");
const nameLoc = document.getElementById('name');
const idLoc = document.getElementById('id');

const loadTime = new Date().getTime();

submitBtn.addEventListener("click", () => {
    getSelected();
});

function getSelected() {
    let id = idLoc.value;
    let name = nameLoc.value;
    let answer = [];
    let errorMessage = "";

    if (name === "") {
        errorMessage += "Namn saknas.\n";
    }
     
    if (id === "") {
        errorMessage += "Id saknas.\n";
    }

    let i = 1;
    let m = false;
    answerEls.forEach((answerEl) => {
        if (i % 2 == 1) {
            m = false;
        }
        if (answerEl.checked) {
            answer.push(answerEl.id);
        } else {
            if (m == true) {
                errorMessage += `Fråga ${i/2} ej besvarad.\n`; 
                m = false;
            } else {
                m = true;
            }
        }
        i += 1;
    });  

    if (errorMessage.length>0) {
        alert(errorMessage);        
    } else {
        let timeSpent = Math.round((new Date().getTime() - loadTime)/1000);
        id = id + "|" + timeSpent        

        // This line fills in a link to a google forms prefilled document.
        // You need to create your own google forms document to gather data.
        window.location.href = `https://docs.google.com/forms/d/e/---ID---/formResponse?usp=pp_url&entry.1939068928=${name}&entry.1173561149=${id}&entry.626477817=${answer[0]}&entry.740914675=${answer[1]}&entry.1281680881=${answer[2]}&entry.1503306834=${answer[3]}&entry.938202907=${answer[4]}&entry.849095064=${answer[5]}&entry.1533616764=${answer[6]}&entry.1675596870=${answer[7]}&entry.117213336=${answer[8]}&entry.1883281661=${answer[9]}&submit=Submit`;
    }
    
}