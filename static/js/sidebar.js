(function($) {
    const win = $(window);
    const body = $('body');
    const leftBtn = $('#leftSidebarToggle');
    const rightBtn = $('#rightSidebarToggle');
    const sendBtn = $('#send-btn')
    const blackBackground = $('.black-background');
    const initialWidth = window.innerWidth;
    const databaseDropdown = document.getElementById("collapseDatabase");
    const settingsDropdown = document.getElementById("collapseSettings");
    const chatBox = document.querySelector('.chatbox');
    const chatInput = document.getElementById("chatInput");
    
    const searchTypeDropdown = document.getElementById('searchTypeDropdown');
    const embeddingModelDropdown = document.getElementById('embeddingModelDropdown');
    const llmModelDropdown = document.getElementById('llmModelDropdown');

    const similaritySlider = $('#similaritySlider');
    const similaritySliderValue = $('#similaritySliderValue');

    const similarityScoreSlider = $('#similarityScoreSlider');
    const similarityScoreSliderValue = $('#similarityScoreSliderValue');
    
    const consideredChunkSlider = $('#consideredChunkSlider');
    const consideredChunkSliderValue = $('#consideredChunkSliderValue');

    const retrievedChunkSlider = $('#retrievedChunkSlider');
    const retrievedChunkSliderValue = $('#retrievedChunkSliderValue');

    const lambdaSlider = $('#lambdaSlider');
    const lambdaSliderValue = $('#lambdaSliderValue');


    let rightWasOpen = true;
    let leftWasOpen = true;
    let resizeTimeout;
    let numberOfDocuments = 0;

    // Initialization
    function init() {
        initSettings(5,90,25,5,25);
        handleResponsiveClasses();
        collapseSidebarsOnLoad();
        bindEvents();
        leftSidebarEvents();
        bindChatEvents();
        ragOptions();
        updateSettings();
        contextCollapseEvents(1)
        databaseDropdown.classList.add('show');
        settingsDropdown.classList.add('show');
        $(function () {
            $('[data-toggle="tooltip"]').tooltip({ boundary: 'window' });
        });
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

    function initSettings(initSimilarityVal, initSimilarityScoreVal, initConsideredVal, initRetrievedVal, initLambdaVal) {
        similaritySliderValue.text(initSimilarityVal);
        similaritySlider.val(initSimilarityVal);

        similarityScoreSliderValue.text(initSimilarityScoreVal);
        similarityScoreSlider.val(initSimilarityScoreVal);

        consideredChunkSliderValue.text(initConsideredVal);
        consideredChunkSlider.val(initConsideredVal);

        retrievedChunkSliderValue.text(initRetrievedVal);
        retrievedChunkSlider.val(initRetrievedVal);

        lambdaSliderValue.text(initLambdaVal);
        lambdaSlider.val(initLambdaVal);
    }

    function leftSidebarEvents() {
        $(document).ready(function() {
            // Open/close menus
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
        });
    }

    function updateSettings() {
        $(document).ready(function() {
            // Sliders
            similaritySlider.on('input', function() {
                similaritySliderValue.text(this.value);
                sendOptions();
            });
            similaritySliderValue.text(similaritySlider.val());

            similarityScoreSlider.on('input', function() {
                similarityScoreSliderValue.text(this.value);
                sendOptions();
            });
            similarityScoreSliderValue.text(similarityScoreSlider.val());

            consideredChunkSlider.on('input', function() {
                consideredChunkSliderValue.text(this.value);
                sendOptions();
            });
            consideredChunkSliderValue.text(consideredChunkSlider.val());

            retrievedChunkSlider.on('input', function() {
                retrievedChunkSliderValue.text(this.value);
                sendOptions();
            });
            retrievedChunkSliderValue.text(retrievedChunkSlider.val());

            lambdaSlider.on('input', function() {
                lambdaSliderValue.text(this.value);
                sendOptions();
            });
            lambdaSliderValue.text(lambdaSlider.val());

            $('#searchTypeDropdown').on('change', function() {
                sendOptions();
            });

            $('#embeddingModelDropdown').on('change', function() {
                sendOptions();
            });

            $('#llmModelDropdown').on('change', function() {
                sendOptions();
            });
        });
    }

    function sendOptions() {
        var rag_settings = {
            embedding_model: embeddingModelDropdown.value,
            llm_model: llmModelDropdown.value,
            search_type: searchTypeDropdown.value,
            similarity_doc_nb: parseInt(similaritySlider.val(), 10),
            score_threshold: parseInt(similarityScoreSlider.val(), 10) / 100,
            considered_chunk: parseInt(consideredChunkSlider.val(), 10),
            mmr_doc_nb: parseInt(retrievedChunkSlider.val(), 10),
            lambda_mult: parseInt(lambdaSlider.val(), 10) / 100
        };

        $.ajax({
            type: "POST",
            url: "/update-settings",
            data: JSON.stringify(rag_settings),
            contentType: "application/json",
            error: function(error) {
                console.error('Error updating settings:', error);
            }
        });
    }

    function ragOptions() {    
        searchTypeDropdown.addEventListener('change', function () {
            var similarity = document.getElementById('similarityContent');
            var similarity_score = document.getElementById('similarityScoreContent');
            var mmr = document.getElementById('mmrContent');
            var elements = [similarity, similarity_score, mmr];
    
            function showElement(element) {
                element.classList.remove('hidden');
                requestAnimationFrame(() => {
                    element.classList.add('fade-enter');
                    requestAnimationFrame(() => {
                        element.classList.add('fade-enter-active');
                    });
                });
    
                element.addEventListener('transitionend', function handleTransitionEnd1(event) {
                    if (event.propertyName === 'opacity') {
                        element.classList.remove('fade-enter', 'fade-enter-active');
                        element.removeEventListener('transitionend', handleTransitionEnd1);
                    }
                });
            }
    
            function hideElement(element, callback) {
                element.classList.add('fade-leave');
                requestAnimationFrame(() => {
                    element.classList.add('fade-leave-active');
                });
    
                element.addEventListener('transitionend', function handleTransitionEnd(event) {
                    if (event.propertyName === 'opacity') {
                        element.classList.remove('fade-leave', 'fade-leave-active');
                        element.classList.add('hidden');
                        element.removeEventListener('transitionend', handleTransitionEnd);
                        if (callback) callback();
                    }
                });
            }
    
            // Function to hide all elements and then show the selected one
            function hideAllAndShowSelected() {
                var elementsToHide = elements.filter(el => !el.classList.contains('hidden'));
                var hideCount = elementsToHide.length;
                var hideCompleteCount = 0;
    
                elementsToHide.forEach(el => hideElement(el, () => {
                    hideCompleteCount++;
                    if (hideCompleteCount === hideCount) {
                        if (searchTypeDropdown.value === 'similarity') {
                            showElement(similarity);
                        } else if (searchTypeDropdown.value === 'similarity_score_threshold') {
                            showElement(similarity_score);
                        } else if (searchTypeDropdown.value === 'mmr') {
                            showElement(mmr);
                        }
                    }
                }));
            }
    
            hideAllAndShowSelected();
        });
    }


    function bindChatEvents() {
        $(document).ready(function() {
            $("#chatInput").on("submit", function(event) {
                event.preventDefault();
                submitQuery();
            });

            $("#chatInput").on("keypress", function(event) {
                if (event.key === "Enter" && chatInput.value != "") {
                    event.preventDefault();
                    submitQuery();
                }
            });
        });
        sendBtn.click(() => {
            if (chatInput.value.trim() != "") {
                submitQuery();
            }
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

            const contextRetriever = document.querySelector('.context-retriever');
            contextRetriever.innerHTML = '';

            for (let i = 0; i < data.context.length; i++) {
                createContextElement(data.context[i].replace(/\n/g, "<br>"), data.source[i], i+1);
            }
            
            waitForElements(data.context.length, () => {
                contextCollapseEvents(data.context.length);
            });
        });
        chatInput.value = "";
        chatInput.style.height = 'auto';
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
