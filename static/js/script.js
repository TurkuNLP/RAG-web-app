document.addEventListener("DOMContentLoaded", function() {
    const win = window;
    const body = document.body;
    const leftBtn = document.getElementById('leftSidebarToggle');
    const rightBtn = document.getElementById('rightSidebarToggle');
    const sendBtn = document.getElementById('send-btn');
    const blackBackground = document.querySelector('.black-background');
    const initialWidth = window.innerWidth;
    const databaseDropdown = document.getElementById("collapseDatabase");
    const settingsDropdown = document.getElementById("collapseSettings");
    const historyDropdown = document.getElementById("collapseHistory");
    const chatBox = document.querySelector('.chatbox');
    const chatInput = document.getElementById("chatInput");
    
    const searchTypeDropdown = document.getElementById('searchTypeDropdown');
    const embeddingModelDropdown = document.getElementById('embeddingModelDropdown');
    const llmModelDropdown = document.getElementById('llmModelDropdown');

    const similaritySlider = document.getElementById('similaritySlider');
    const similaritySliderValue = document.getElementById('similaritySliderValue');
    const maxChunkSlider = document.getElementById('maxChunkSlider');
    const maxChunkSliderValue = document.getElementById('maxChunkSliderValue');

    const similarityScoreSlider = document.getElementById('similarityScoreSlider');
    const similarityScoreSliderValue = document.getElementById('similarityScoreSliderValue');
    
    const consideredChunkSlider = document.getElementById('consideredChunkSlider');
    const consideredChunkSliderValue = document.getElementById('consideredChunkSliderValue');

    const retrievedChunkSlider = document.getElementById('retrievedChunkSlider');
    const retrievedChunkSliderValue = document.getElementById('retrievedChunkSliderValue');

    const lambdaSlider = document.getElementById('lambdaSlider');
    const lambdaSliderValue = document.getElementById('lambdaSliderValue');

    const historySwitchBtn = document.getElementById('flexSwitchHistory');
    const clearHistoryBtn = document.getElementById('clear-btn');

    let rightWasOpen = true;
    let leftWasOpen = true;
    let resizeTimeout;
    let searchNumber = 0;
    let storedChunks = 0;

    // Initialization
    function init() {
        initSettings('similarity', 5, 80, 5, 25, 5, 25, 'voyage-multilingual-2', 'gpt-3.5-turbo');
        clearChatHistory(onLoad = true);
        handleResponsiveClasses();
        collapseSidebarsOnLoad();
        bindEvents();
        bindChatEvents();
        ragOptions();
        updateSettings();
        contextCollapseEvents(1);
        initTooltips();
        databaseDropdown.classList.add('show');
        settingsDropdown.classList.add('show');
        historyDropdown.classList.add('show');
        leftSidebarEvents();
        fetchDocuments();
        hideOverlay();
    }

    function initTooltips() {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });        
    }

    function collapseSidebarsOnLoad() {
        const width = win.innerWidth;
        if (width < 992) {
            body.classList.add('left-sidebar-closed');
        }
        if (width < 576) {
            body.classList.add('left-sidebar-closed', 'right-sidebar-closed');
        }
    }

    function bindEvents() {
        leftBtn.addEventListener('click', () => toggleSidebar('left'));
        rightBtn.addEventListener('click', () => toggleSidebar('right'));
        blackBackground.addEventListener('click', () => toggleSidebar('left'));
        clearHistoryBtn.addEventListener('click', () => clearChatHistory());

        document.addEventListener("visibilitychange", handleVisibilityChange);
        win.addEventListener('resize', () => {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(handleResponsiveClasses, 20);
        });

        if (chatInput) {
            chatInput.addEventListener('input', adjustTextareaHeight);
        }
    }

    function contextCollapseEvents(numberOfDocuments) {
        for (let i = 1; i <= numberOfDocuments; i++) {
            const collapseId = `collapse${i}`;
            const headingId = `heading${i}`;
            const collapseElement = document.getElementById(collapseId);
            const headingElement = document.getElementById(headingId);
            if (collapseElement && headingElement) {
                collapseElement.addEventListener('show.bs.collapse', () => {
                    headingElement.classList.add('collapse-open');
                });
                collapseElement.addEventListener('hide.bs.collapse', () => {
                    setTimeout(() => {
                        headingElement.classList.remove('collapse-open');
                    }, 300);
                });
            } else {
                console.warn(`Elements with IDs ${collapseId} or ${headingId} do not exist.`);
            }
        }
    }

    function initSettings(initSearchType, initSimilarityVal, initSimilarityScoreVal, initMaxChunkValue, initConsideredVal, initRetrievedVal, initLambdaVal, initEmbedding, initLLM) {
        searchTypeDropdown.value = initSearchType;
        
        similaritySliderValue.textContent = initSimilarityVal;
        similaritySlider.value = initSimilarityVal;

        similarityScoreSliderValue.textContent = initSimilarityScoreVal;
        similarityScoreSlider.value = initSimilarityScoreVal;

        maxChunkSliderValue.textContent = initMaxChunkValue;
        maxChunkSlider.value = initMaxChunkValue;

        consideredChunkSliderValue.textContent = initConsideredVal;
        consideredChunkSlider.value = initConsideredVal;

        retrievedChunkSliderValue.textContent = initRetrievedVal;
        retrievedChunkSlider.value = initRetrievedVal;

        lambdaSliderValue.textContent = initLambdaVal;
        lambdaSlider.value = initLambdaVal;

        embeddingModelDropdown.value = initEmbedding;

        llmModelDropdown.value = initLLM;
    }

    function leftSidebarEvents() {
        const collapseSettings = document.getElementById('collapseSettings');
        const collapseHistory = document.getElementById('collapseHistory');
        const collapseDatabase = document.getElementById('collapseDatabase');
        if (collapseSettings){
            collapseSettings.addEventListener('show.bs.collapse', () => {
                document.querySelector('.settings-header').classList.add('collapse-open');
            });

            collapseSettings.addEventListener('hide.bs.collapse', () => {
                setTimeout(() => {
                    document.querySelector('.settings-header').classList.remove('collapse-open');
                }, 300);
            });
        } else {
            console.warn(`Elements with IDs collapseSettings do not exist.`);
        }

        if (collapseHistory) {
            collapseHistory.addEventListener('show.bs.collapse', () => {
                document.querySelector('.history-header').classList.add('collapse-open');
            });

            collapseHistory.addEventListener('hide.bs.collapse', () => {
                setTimeout(() => {
                    document.querySelector('.history-header').classList.remove('collapse-open');
                }, 300);
            });            
        } else {
            console.warn(`Elements with IDs collapseHistory do not exist.`);
        }

        if (collapseDatabase) {
            collapseDatabase.addEventListener('show.bs.collapse', () => {
                document.querySelector('.database-header').classList.add('collapse-open');
            });

            collapseDatabase.addEventListener('hide.bs.collapse', () => {
                setTimeout(() => {
                    document.querySelector('.database-header').classList.remove('collapse-open');
                }, 300);
            });            
        } else {
            console.warn(`Elements with IDs collapseDatabase do not exist.`);
        }

    }

    function updateSettings() {
        similaritySlider.addEventListener('input', function() {
            similaritySliderValue.textContent = this.value;
            sendOptions();
        });
        similaritySliderValue.textContent = similaritySlider.value;

        similarityScoreSlider.addEventListener('input', function() {
            similarityScoreSliderValue.textContent = this.value;
            sendOptions();
        });
        similarityScoreSliderValue.textContent = similarityScoreSlider.value;

        maxChunkSlider.addEventListener('input', function() {
            maxChunkSliderValue.textContent = maxChunkSlider.value;
            sendOptions();
        });
        maxChunkSliderValue.textContent = maxChunkSlider.value;

        consideredChunkSlider.addEventListener('input', function() {
            consideredChunkSliderValue.textContent = this.value;
            sendOptions();
        });
        consideredChunkSliderValue.textContent = consideredChunkSlider.value;

        retrievedChunkSlider.addEventListener('input', function() {
            retrievedChunkSliderValue.textContent = this.value;
            sendOptions();
        });
        retrievedChunkSliderValue.textContent = retrievedChunkSlider.value;

        lambdaSlider.addEventListener('input', function() {
            lambdaSliderValue.textContent = this.value;
            sendOptions();
        });
        lambdaSliderValue.textContent = lambdaSlider.value;

        searchTypeDropdown.addEventListener('change', function() {
            sendOptions();
        });

        embeddingModelDropdown.addEventListener('change', function() {
            sendOptions();
        });

        llmModelDropdown.addEventListener('change', function() {
            sendOptions();
        });

        historySwitchBtn.addEventListener('change', function() {
            sendOptions();
        });
    }

    function sendOptions() {
        var rag_settings = {
            embedding_model: embeddingModelDropdown.value,
            llm_model: llmModelDropdown.value,
            search_type: searchTypeDropdown.value,
            similarity_doc_nb: parseInt(similaritySlider.value, 10),
            score_threshold: parseInt(similarityScoreSlider.value, 10) / 100,
            max_chunk_return: parseInt(maxChunkSlider.value, 10),
            considered_chunk: parseInt(consideredChunkSlider.value, 10),
            mmr_doc_nb: parseInt(retrievedChunkSlider.value, 10),
            lambda_mult: parseInt(lambdaSlider.value, 10) / 100,
            isHistoryOn : historySwitchBtn.checked
        };
        fetch(`${root}/update-settings`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(rag_settings)
        }).catch(error => {
            console.error('Error updating settings:', error);
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
        chatInput.addEventListener("submit", function(event) {
            event.preventDefault();
            submitQuery();
        });

        chatInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter" && chatInput.value !== "") {
                event.preventDefault();
                submitQuery();
            }
        });

        sendBtn.addEventListener('click', () => {
            if (chatInput.value.trim() !== "") {
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
        const width = win.innerWidth;
        body.classList.remove('small', 'medium', 'large');

        if (width < 576) {
            body.classList.add('small', 'left-sidebar-closed', 'right-sidebar-closed');
        } else if (width >= 576 && width < 992) {
            blackBackground.classList.add('hidden');
            body.classList.add('medium');
            if (rightWasOpen) {
                body.classList.remove('right-sidebar-closed');
                body.classList.add('left-sidebar-closed');
            } else if (leftWasOpen) {
                body.classList.remove('left-sidebar-closed');
                body.classList.add('right-sidebar-closed');
            }
        } else {
            blackBackground.classList.add('hidden');
            body.classList.add('large');
            body.classList.toggle('left-sidebar-closed', !leftWasOpen);
            body.classList.toggle('right-sidebar-closed', !rightWasOpen);
        }
    }

    function toggleSidebar(side) {
        const isSmall = body.classList.contains('small');
        const isMedium = body.classList.contains('medium');
        const isClosed = body.classList.contains(`${side}-sidebar-closed`);
        const oppositeSide = side === 'left' ? 'right' : 'left';
        const isOppositeClosed = body.classList.contains(`${oppositeSide}-sidebar-closed`);

        if (isSmall || isMedium) {
            if (isClosed) {
                if (!isOppositeClosed) {
                    body.classList.add(`${oppositeSide}-sidebar-closed`);
                }
                body.classList.remove(`${side}-sidebar-closed`);
                if (isSmall && side === 'left') {
                    blackBackground.classList.remove('hidden');
                }
            } else {
                body.classList.add(`${side}-sidebar-closed`);
                if (isSmall && side === 'left') {
                    blackBackground.classList.add('hidden');
                }
            }
        } else {
            if (isClosed) {
                body.classList.remove(`${side}-sidebar-closed`);
            } else {
                body.classList.add(`${side}-sidebar-closed`);
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
        cardHeader.id = `heading${contextNumber}`;

        const span = document.createElement('span');
        span.className = 'float-start mx-2';

        const doc = await fetchDocument(source);
        if (doc) {
            const docIcon = createIcon(doc);
            span.appendChild(docIcon);
            span.appendChild(document.createTextNode(source));

            const downloadButton = createLink(doc);
            downloadButton.textContent = "";

            const downloadIcon = document.createElement('img');
            downloadIcon.classList.add('icon');
            downloadIcon.classList.add('download-icon');
            downloadIcon.src = `${root}/static/img/download.svg`;

            downloadButton.appendChild(downloadIcon);
            cardHeader.appendChild(downloadButton);
        } else {
            console.error('Document is undefined');
        }

        const contextButton = document.createElement('button');
        contextButton.className = 'btn btn-menu text-white context';
        contextButton.type = 'button';
        contextButton.setAttribute('data-bs-toggle', 'collapse');
        contextButton.setAttribute('data-bs-target', `#collapse${contextNumber}`);
        contextButton.setAttribute('aria-expanded', 'true');
        contextButton.setAttribute('aria-controls', `collapse${contextNumber}`);

        const caretIcon = document.createElement('i');
        caretIcon.className = 'fas fa-caret-down float-end';

        contextButton.appendChild(span);
        contextButton.appendChild(caretIcon);
        cardHeader.appendChild(contextButton);

        const collapseDiv = document.createElement('div');
        collapseDiv.id = `collapse${contextNumber}`;
        collapseDiv.className = 'collapse';
        collapseDiv.setAttribute('aria-labelledby', `heading${contextNumber}`);

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body text-white text-justify';
        cardBody.innerHTML = context;

        collapseDiv.appendChild(cardBody);

        const container = document.querySelector('.context-retriever');
        container.appendChild(cardHeader);
        container.appendChild(collapseDiv);
    }

    function createSearchNumberElement() {
        const contextRetriever = document.querySelector('.context-retriever');
        if (searchNumber === 0) {
            contextRetriever.innerHTML = '';
        }
        const cardHeader = document.createElement('div');
        cardHeader.className = 'card-header search-card';

        searchNumber += 1;

        const span = document.createElement('span');
        span.className = 'float-start mx-2 text-white';
        span.textContent = `Search ${searchNumber}`;

        cardHeader.appendChild(span);
        contextRetriever.appendChild(cardHeader);
    }

    function submitQuery() {
        const userMessage = chatInput.value.trim();
        chatBox.appendChild(createChatLi(userMessage, "outcoming"));
        fetch(`${root}/get`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ msg: userMessage })
        }).then(response => response.json())
        .then(data => {
            chatBox.appendChild(createChatLi(data.response, "incoming"));
            chatBox.scrollTo(0, chatBox.scrollHeight);

            createSearchNumberElement();

            for (let i = 0; i < data.context.length; i++) {
                createContextElement(data.context[i].replace(/\n/g, "<br>"), data.source[i], storedChunks + i + 1);
            }
            
            storedChunks += data.context.length;

            waitForElements(data.context.length, () => {
                contextCollapseEvents(storedChunks);
            });
        });
        chatInput.value = "";
        chatInput.style.height = 'auto';
    }

    function clearChatHistory(onLoad = false) {
        fetch(`${root}/clear_chat_history`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if(!onLoad) {
                const contextRetriever = document.querySelector('.context-retriever');
                contextRetriever.innerHTML = '';
                chatBox.innerHTML = '';
                searchNumber = 0;
                storedChunks = 0;        
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    }

    function waitForElements(numberOfDocuments, callback) {
        const interval = setInterval(() => {
            let allExist = true;
            for (let i = 1; i <= numberOfDocuments; i++) {
                const collapseId = `#collapse${i}`;
                const headingId = `#heading${i}`;
                if (!document.querySelector(collapseId) || !document.querySelector(headingId)) {
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
                icon.src = `${root}/static/img/pdf.svg`;
                break;
            case 'docs':
                icon.src = `${root}/static/img/doc.svg`;
                break;
            case 'txt':
                icon.src = `${root}/static/img/txt.svg`;
                break;
            case 'csv':
                icon.src = `${root}/static/img/csv.svg`;
                break;

            default:
                icon.src = `${root}/static/img/doc.svg`;
        }
        return icon;
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
        const response = await fetch(`${root}/documents`);
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
            const response = await fetch(`${root}/documents/${documentName}`);
            if (!response.ok) {
                throw new Error('Document not found');
            }
            const doc = await response.json();
            return doc;
        } catch (error) {
            console.error('Error fetching document:', error);
        }
    }

    window.onload = function() {
        init();
    };

});
