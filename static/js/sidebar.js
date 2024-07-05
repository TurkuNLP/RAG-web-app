(function($) {
    const win = $(window);
    const body = $('body');
    const leftBtn = $('#leftSidebarToggle');
    const rightBtn = $('#rightSidebarToggle');
    const leftSidebar = $('.sidebar-left');
    const rightSidebar = $('.sidebar-right');
    const blackBackground = $('.black-background');
    const initialWidth = window.innerWidth;
    const databaseDropdown = document.getElementById("collapseDatabase");
    const settingsDropdown = document.getElementById("collapseSettings");
    const chatBox = document.querySelector('.chatbox');
    const chatInput = document.getElementById("chatInput");

    let rightWasOpen = true;
    let leftWasOpen = true;
    let resizeTimeout;
    let numberOfDocuments = 0;

    // Initialization
    function init() {
        initSettings(5,90);
        handleResponsiveClasses();
        collapseSidebarsOnLoad();
        bindEvents();
        leftSidebarEvents();
        bindChatEvents();
        databaseDropdown.classList.add('show');
        settingsDropdown.classList.add('show');
    }

    function collapseSidebarsOnLoad() {
        const width = win.width();
        if (width < 992) {
            body.addClass('left-sidebar-closed');
        }
        if (width < 576) {
            body.addClass('left-sidebar-closed right-sidebar-closed');
        }
    }

    function bindEvents() {
        leftBtn.click(() => toggleSidebar('left'));
        rightBtn.click(() => toggleSidebar('right'));
        blackBackground.click(() => toggleSidebar('left'));

        document.addEventListener("DOMContentLoaded", hideOverlay);
        document.addEventListener('visibilitychange', handleVisibilityChange);
        win.resize(() => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(handleResponsiveClasses, 20);
        });

        if (chatInput) {
            chatInput.addEventListener('input', adjustTextareaHeight);
        }
    }

    function contextCollapseEvents(numberOfDocuments) {
        $(document).ready(function() {
            for (let i = 1; i <= numberOfDocuments; i++) {
                const collapseId = `#collapse${i}`;
                const headingId = `#heading${i}`;
                if ($(collapseId).length && $(headingId).length) {
                    $(collapseId).on('show.bs.collapse', function() {
                        $(headingId).addClass('collapse-open');
                    }).on('hide.bs.collapse', function() {
                        setTimeout(() => {
                            $(headingId).removeClass('collapse-open');
                        }, 300);
                    });
                } else {
                    console.warn(`Elements with IDs ${collapseId} or ${headingId} do not exist.`);
                }
            }            
        });
    }

    function initSettings(initSliderValue, initPrecisionValue) {
        const chunkSlider = $('#chunkSlider');
        const chunkSliderValue = $('#chunkSliderValue');
        chunkSliderValue.text(initSliderValue)
        chunkSlider.val(initSliderValue)

        const precisionSlider = $('#precisionSlider');
        const precisionSliderValue = $('#precisionSliderValue');
        precisionSliderValue.text(initPrecisionValue);
        precisionSlider.val(initPrecisionValue);
    }

    function leftSidebarEvents() {
        $(document).ready(function() {
            $('#collapseSettings').on('show.bs.collapse', function() {
                $('.settings-header').addClass('collapse-open');
            }).on('hide.bs.collapse', function() {
                setTimeout(() => {
                    $('.settings-header').removeClass('collapse-open');
                }, 300);
            });
    
            $('#collapseDatabase').on('show.bs.collapse', function() {
                $('.database-header').addClass('collapse-open');
            }).on('hide.bs.collapse', function() {
                setTimeout(() => {
                    $('.database-header').removeClass('collapse-open');
                }, 300);
            });
    
            const chunkSlider = $('#chunkSlider');
            const chunkSliderValue = $('#chunkSliderValue');
            chunkSlider.on('input', function() {
                chunkSliderValue.text(this.value);
            });
            chunkSliderValue.text(chunkSlider.val());
    
            const precisionSlider = $('#precisionSlider');
            const precisionSliderValue = $('#precisionSliderValue');
            precisionSlider.on('input', function() {
                precisionSliderValue.text(this.value);
            });
            precisionSliderValue.text(precisionSlider.val());
        });
    }

    function bindChatEvents() {
        $(document).ready(function() {
            $("#chatInput").on("submit", function(event) {
                event.preventDefault();
                submitQuery();
            });

            $("#chatInput").on("keypress", function(event) {
                if (event.key === "Enter") {
                    event.preventDefault();
                    submitQuery();
                }
            });
        });
    }

    function hideOverlay() {
        const overlay = document.getElementById("overlay");
        setTimeout(() => {
            overlay.classList.add("hidden");
        }, 500);
    }

    function handleVisibilityChange() {
        if (document.visibilityState === 'visible' && window.innerWidth !== initialWidth) {
            const overlay = document.getElementById("overlay");
            overlay.classList.remove("hidden");
            setTimeout(() => {
                overlay.classList.add("hidden");
                window.dispatchEvent(new Event('resize'));
            }, 500);
        }
    }

    function handleResponsiveClasses() {
        const width = win.width();
        body.removeClass('small medium large');

        if (width < 576) {
            body.addClass('small left-sidebar-closed right-sidebar-closed');
        } else if (width >= 576 && width < 992) {
            blackBackground.addClass('hidden');
            body.addClass('medium');
            if (rightWasOpen) {
                body.removeClass('right-sidebar-closed').addClass('left-sidebar-closed');
            } else if (leftWasOpen) {
                body.removeClass('left-sidebar-closed').addClass('right-sidebar-closed');
            }
        } else {
            blackBackground.addClass('hidden');
            body.addClass('large');
            body.toggleClass('left-sidebar-closed', !leftWasOpen);
            body.toggleClass('right-sidebar-closed', !rightWasOpen);
        }
    }

    function toggleSidebar(side) {
        const isSmall = body.hasClass('small');
        const isMedium = body.hasClass('medium');
        const isClosed = body.hasClass(`${side}-sidebar-closed`);
        const sidebar = side === 'left' ? leftSidebar : rightSidebar;
        const oppositeSide = side === 'left' ? 'right' : 'left';
        const isOppositeClosed = body.hasClass(`${oppositeSide}-sidebar-closed`);

        if (isSmall || isMedium) {
            if (isClosed) {
                if (!isOppositeClosed) {
                    body.addClass(`${oppositeSide}-sidebar-closed`);
                }
                body.removeClass(`${side}-sidebar-closed`);
                if (isSmall && side === 'left') {
                    blackBackground.removeClass('hidden');
                }
            }
            else {
                body.addClass(`${side}-sidebar-closed`);
                if (isSmall && side === 'left') {
                    blackBackground.addClass('hidden');
                }
            }
        }
        else {
            if (isClosed) {
                body.removeClass(`${side}-sidebar-closed`);
            }
            else {
                body.addClass(`${side}-sidebar-closed`);
            }
        }

        if (side === 'left') {
            if (!(isClosed && leftWasOpen)) {
                leftWasOpen = !leftWasOpen;
            }
        } else {
            if (!(isClosed && rightWasOpen)) {
                rightWasOpen = !rightWasOpen;
            }
        }
    }

    function adjustTextareaHeight(event) {
        const textarea = event.target;
        textarea.style.height = 'auto';
        textarea.style.height = `${textarea.scrollHeight}px`;
        const maxHeight = parseFloat(window.getComputedStyle(textarea).maxHeight);
        if (textarea.scrollHeight > maxHeight) {
            textarea.style.height = `${maxHeight}px`;
        }
    }

    function createChatLi(message, className) {
        const chatLi = document.createElement("li");
        chatLi.classList.add("message", className);
        chatLi.innerHTML = message;
        return chatLi;
    }

    async function createContextElement(context, source, contextNumber) {
        const cardHeader = document.createElement('div');
        cardHeader.className = 'card-header';
        cardHeader.id = `heading${contextNumber}`

        const span = document.createElement('span');
        span.className = 'float-left mx-2';

        const doc = await fetchDocument(source);
        if(doc) {
            const docIcon = createIcon(doc);
            span.appendChild(docIcon);
            span.appendChild(document.createTextNode(source));

            const downloadButton = createLink(doc);
            downloadButton.textContent = "";

            const downloadIcon = document.createElement('img');
            downloadIcon.classList.add('icon');
            downloadIcon.classList.add('download-icon');
            downloadIcon.src = 'static/img/download.svg';

            downloadButton.appendChild(downloadIcon);
            cardHeader.appendChild(downloadButton);
        } 
        else {
            console.error('Document is undefined');
        }

        const contextButton = document.createElement('button');
        contextButton.className = 'btn btn-link text-white context';
        contextButton.type = 'button';
        contextButton.setAttribute('data-toggle', 'collapse');
        contextButton.setAttribute('data-target', `#collapse${contextNumber}`);
        contextButton.setAttribute('aria-expanded', 'true');
        contextButton.setAttribute('aria-controls', `#collapse${contextNumber}`);

        const caretIcon = document.createElement('i');
        caretIcon.className = 'fas fa-caret-down float-right';
    
        contextButton.appendChild(span);
        contextButton.appendChild(caretIcon);
        cardHeader.appendChild(contextButton);
    
        const collapseDiv = document.createElement('div');
        collapseDiv.id = `collapse${contextNumber}`;
        collapseDiv.className = 'collapse';
        collapseDiv.setAttribute('aria-labelledby', `heading${contextNumber}`);
    
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body text-white text-justify';
        cardBody.innerHTML = context

        collapseDiv.appendChild(cardBody);
    
        const container = document.querySelector('.context-retriever');
        container.appendChild(cardHeader);
        container.appendChild(collapseDiv);
    }

    function submitQuery() {
        const userMessage = chatInput.value.trim();
        chatBox.appendChild(createChatLi(userMessage, "outcoming"));
        $.ajax({
            data: { msg: userMessage },
            type: "POST",
            url: "/get",
        }).done(function(data) {
            chatBox.appendChild(createChatLi(data.response, "incoming"));
            chatBox.scrollTo(0, chatBox.scrollHeight);

            for (let i = 0; i < data.context.length; i++) {
                createContextElement(data.context[i].replace(/\n/g, "<br>"), data.source[i], i+1);
            }
            
            waitForElements(data.context.length, () => {
                contextCollapseEvents(data.context.length);
            });
        });
        chatInput.value = "";
    }

    function waitForElements(numberOfDocuments, callback) {
        const interval = setInterval(() => {
            let allExist = true;
            for (let i = 1; i <= numberOfDocuments; i++) {
                const collapseId = `#collapse${i}`;
                const headingId = `#heading${i}`;
                if (!$(collapseId).length || !$(headingId).length) {
                    allExist = false;
                    break;
                }
            }
            if (allExist) {
                clearInterval(interval);
                callback();
            }
        }, 100);
    }
    

    function createIcon(doc) {
        const icon = document.createElement('img');
        icon.classList.add('icon');
    
        switch (doc.extension.toLowerCase()) {
            case 'pdf':
                icon.src = 'static/img/pdf.svg';
                break;
            case 'docs':
                icon.src = 'static/img/doc.svg';
                break;
            case 'txt':
                icon.src = 'static/img/txt.svg';
                break;
            case 'csv':
                icon.src = 'static/img/csv.svg';
                break;
    
            default:
                icon.src = 'static/img/doc.svg';
        }
        return icon
    }

    function createLink(doc) {
        const link = document.createElement('a');
        link.href = doc.url;
        link.textContent = doc.name;
        link.title = doc.name;
        link.target = "_blank";
    
        return link;
    }

    async function fetchDocuments() {
        const response = await fetch('/documents');
        const documents = await response.json();
        const listElement = document.querySelector('.database');

        documents.sort((a, b) => a.name.localeCompare(b.name)); // Alphabetical sort

        documents.forEach(doc => {
            const listItem = document.createElement('li');
            listItem.classList.add("database-item");
            
            const icon = createIcon(doc);
            const link = createLink(doc);
        
            listItem.appendChild(icon);
            listItem.appendChild(link);
            listElement.appendChild(listItem);
        });
    }

    async function fetchDocument(documentName) {
        try {
            const response = await fetch(`/documents/${documentName}`);
            if (!response.ok) {
                throw new Error('Document not found');
            }
            const doc = await response.json();
            return doc;
        } catch (error) {
            console.error('Error fetching document:', error);
        }
    }

    
    window.onload = fetchDocuments;

    // Initial call to set the classes and bind events
    init();
})(jQuery);
