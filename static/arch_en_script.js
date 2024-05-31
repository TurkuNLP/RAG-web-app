const body = document.querySelector("body"),
leftSidebar = body.querySelector(".left-sidebar"),
toggleLeft = body.querySelector(".toggle"),
rightSidebar = body.querySelector(".right-sidebar"),
toggleRight = body.querySelector(".toggle-right"),
modeText = body.querySelector(".mode-text"),
chatBox = body.querySelector(".chatbox"),
chatInput = body.querySelector(".chat-text"),
sendBtn = body.querySelector(".chat-input button"),
context = body.querySelector(".context-text"),
source = body.querySelector(".source-text");

let userMessage;


document.addEventListener('DOMContentLoaded', function() {
    // Open the right-sidebar when page is loaded/reloaded and window size > 768
    if (window.innerWidth > 768) {
        rightSidebar.classList.toggle("right-close");
        leftSidebar.classList.toggle("right-close");
        rightSidebar.classList.toggle("left-close");
        leftSidebar.classList.toggle("left-close");
    }
    fetchDocuments;
});

window.addEventListener("resize", function() {
    // Gestion of sidebar when windows is getting resized
    if (window.innerWidth < 768) {
        if (!rightSidebar.classList.contains("right-close")) {
            leftSidebar.classList.toggle("right-close");
            rightSidebar.classList.toggle("right-close");      
        }
        if (!rightSidebar.classList.contains("left-close")) {
            leftSidebar.classList.toggle("left-close");
            rightSidebar.classList.toggle("left-close");                 
        }
    }
    else if (window.innerWidth < 1024) {
        if (!rightSidebar.classList.contains("right-close") && !rightSidebar.classList.contains("left-close")) {
            leftSidebar.classList.toggle("left-close");
            rightSidebar.classList.toggle("left-close");       
        }
    }
});


toggleLeft.addEventListener("click", () => {
    if (window.innerWidth <= 1024) {
        rightSidebar.classList.add("right-close");
        leftSidebar.classList.add("right-close");
    }
    rightSidebar.classList.toggle("left-close");
    leftSidebar.classList.toggle("left-close");
});

toggleRight.addEventListener("click", () => {
    if (window.innerWidth <= 1024) {
        leftSidebar.classList.add("left-close");
        rightSidebar.classList.add("left-close");
    }
    rightSidebar.classList.toggle("right-close");
    leftSidebar.classList.toggle("right-close");
});

const createChatLi = (message, className) => {
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", className);
    let chatContent = className === "incoming" ? `<span class="material-symbols-outlined"><i class='bx bxs-message-dots'></i></span><p>${message}</p>` : `<p>${message}</p>`;
    chatLi.innerHTML = chatContent;
    return chatLi;
};

const handleChat = () => {
    userMessage = chatInput.value.trim();
    console.log(userMessage)
    if(!userMessage) return;

    // Append the user's message to the chatbox
    chatBox.appendChild(createChatLi(userMessage, "outgoing"));
    chatBox.scrollTo(0, chatBox.scrollHeight);

    setTimeout(() => {
        // Display "Thinking..." message while waiting for the response
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatBox.appendChild(incomingChatLi);
        chatBox.scrollTo(0, chatBox.scrollHeight);
    }, 600);

};

$(document).ready(function() {
    function submitQuerry() {
        userMessage = chatInput.value.trim();
        console.log(userMessage);
        chatBox.appendChild(createChatLi(userMessage, "outgoing"));
        $.ajax({
            data: {
                msg: userMessage,
            },
            type: "POST",
            url: "/arch-en/get",
        }).done(function(data) {
            chatBox.appendChild(createChatLi(data.response, "incoming"));
            chatBox.scrollTo(0, chatBox.scrollHeight);
            context.innerHTML = "";
            source.innerHTML = "";
            
            let counter = 1;
            data.context.forEach(function(ctx){
                context.innerHTML += "Chunk " + counter + " :<br><br>" + ctx.replace(/\n/g,"<br>") + "<br><br>";
                counter++;
            })
            
            data.source.forEach(function(src) {
                source.innerHTML += src + "<br>";
            });
        });
        event.preventDefault();
        chatInput.value = "";
    }

    $("#message-area").on("submit", function(event) {
        event.preventDefault();
        submitQuerry();
    });

    $("#message-area").on("keypress", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            submitQuerry();            
        }
    });
});

// Function to get documents from server
async function fetchDocuments() {
    const response = await fetch('/arch-en/documents');
    const documents = await response.json();
    const listElement = document.getElementById('document-list');

    documents.forEach(doc => {
        const listItem = document.createElement('li');
        const link = document.createElement('a');
        link.href = doc.url;
        link.textContent = doc.name;
        link.title = doc.name;
        link.target = "_blank";
        
        const icon = document.createElement('img');
        icon.classList.add('icon');
        switch (doc.extension) {
            case 'pdf':
                icon.src = 'arch-en/static/document-pdf.svg';
                break;

            case 'docs':
                icon.src = 'static/microsoft-word.svg';
                break;                        
        
            default:
                icon.src = 'arch-ru/static/microsoft-word.svg';
        }
        listItem.appendChild(icon);
        listItem.appendChild(link);
        listElement.appendChild(listItem);
    });
}
window.onload = fetchDocuments;