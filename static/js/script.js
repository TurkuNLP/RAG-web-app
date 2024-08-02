document.addEventListener("DOMContentLoaded", function() {
    // Elements and variables initialization
    const win = window;
    const body = document.body;
    const leftBtn = document.getElementById('leftSidebarToggle');
    const rightBtn = document.getElementById('rightSidebarToggle');
    const sendBtn = document.getElementById('send-btn');
    const blackBackground = document.querySelector('.black-background');
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

    /**
     * Initializes the main settings and elements when the page is loaded.
     */
    function init() {
        initializeDefaultSettings('similarity', 5, 80, 5, 25, 5, 25, 'openai', 'gpt-3.5-turbo');
        clearChatHistory(true);
        handleResponsiveClasses();
        collapseSidebarsOnLoad();
        bindEvents();
        bindChatEvents();
        configureRagOptions();
        updateSettings();
        setupContextCollapseEvents(1);
        initTooltips();
        databaseDropdown.classList.add('show');
        settingsDropdown.classList.add('show');
        historyDropdown.classList.add('show');
        leftSidebarEvents();
        loadDocuments();
        hideOverlay();
    }

    /**
     * Initializes Bootstrap tooltips for the page.
     */
    function initTooltips() {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    /**
     * Handles the collapse state of sidebars based on the window width at page load.
     */
    function collapseSidebarsOnLoad() {
        const width = win.innerWidth;
        if (width < 992) {
            body.classList.add('left-sidebar-closed');
        }
        if (width < 576) {
            body.classList.add('left-sidebar-closed', 'right-sidebar-closed');
        }
    }

    /**
     * Binds various UI events to their corresponding event handlers.
     */
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

    /**
     * Sets up default settings for search options and models.
     * @param {string} initSearchType - The default search type.
     * @param {number} initSimilarityVal - The default similarity value.
     * @param {number} initSimilarityScoreVal - The default similarity score threshold.
     * @param {number} initMaxChunkValue - The default maximum chunk return value.
     * @param {number} initConsideredVal - The default considered chunk value.
     * @param {number} initRetrievedVal - The default number of retrieved chunks.
     * @param {number} initLambdaVal - The default lambda multiplier value.
     * @param {string} initEmbedding - The default embedding model.
     * @param {string} initLLM - The default large language model.
     */
    function initializeDefaultSettings(initSearchType, initSimilarityVal, initSimilarityScoreVal, initMaxChunkValue, initConsideredVal, initRetrievedVal, initLambdaVal, initEmbedding, initLLM) {
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

    /**
     * Binds events related to the left sidebar elements, such as settings and history.
     */
    function leftSidebarEvents() {
        const collapseSettings = document.getElementById('collapseSettings');
        const collapseHistory = document.getElementById('collapseHistory');
        const collapseDatabase = document.getElementById('collapseDatabase');
        if (collapseSettings) {
            collapseSettings.addEventListener('show.bs.collapse', () => {
                document.querySelector('.settings-header').classList.add('collapse-open');
            });
            collapseSettings.addEventListener('hide.bs.collapse', () => {
                setTimeout(() => {
                    document.querySelector('.settings-header').classList.remove('collapse-open');
                }, 300);
            });
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
        }
    }

    /**
     * Updates the settings based on user interactions with the UI elements.
     */
    function updateSettings() {
        similaritySlider.addEventListener('input', function() {
            similaritySliderValue.textContent = this.value;
            submitSettingsToServer();
        });
        similarityScoreSlider.addEventListener('input', function() {
            similarityScoreSliderValue.textContent = this.value;
            submitSettingsToServer();
        });
        maxChunkSlider.addEventListener('input', function() {
            maxChunkSliderValue.textContent = maxChunkSlider.value;
            submitSettingsToServer();
        });
        consideredChunkSlider.addEventListener('input', function() {
            consideredChunkSliderValue.textContent = this.value;
            submitSettingsToServer();
        });
        retrievedChunkSlider.addEventListener('input', function() {
            retrievedChunkSliderValue.textContent = this.value;
            submitSettingsToServer();
        });
        lambdaSlider.addEventListener('input', function() {
            lambdaSliderValue.textContent = this.value;
            submitSettingsToServer();
        });
        searchTypeDropdown.addEventListener('change', function() {
            submitSettingsToServer();
        });
        embeddingModelDropdown.addEventListener('change', function() {
            submitSettingsToServer();
        });
        llmModelDropdown.addEventListener('change', function() {
            submitSettingsToServer();
        });
        historySwitchBtn.addEventListener('change', function() {
            submitSettingsToServer();
        });
    }

    /**
     * Submits the updated settings to the server.
     */
    function submitSettingsToServer() {
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

    /**
     * Binds events related to the chat functionality, such as sending messages.
     */
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
    /** 
     * Manages the visibility of different context panels
     * @param {number} newDocs - The number of new context windows to configure.
     * @param {number} numberOfDocumentsBefore - Previous number of documents.
     */
    function setupContextCollapseEvents(newDocs, numberOfDocumentsBefore) {
        for (let docNum = numberOfDocumentsBefore+1; docNum <= numberOfDocumentsBefore+newDocs; docNum++) {
            const collapseId = `collapse${docNum}`;
            const headingId = `heading${docNum}`;
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
            }
        }
    }

    /** 
     * Binds the close event on click for all close buttons
     * @param {number} newDocs - The number of new close buttons to configure.
     * @param {number} numberOfDocumentsBefore - Previous number of documents.
     */
    function setupCloseEventListener(newDocs, numberOfDocumentsBefore) {
        for (let docNum = numberOfDocumentsBefore+1; docNum <= numberOfDocumentsBefore+newDocs; docNum++) {
            const closeButton = document.getElementById(`close${docNum}`);
            if (closeButton) {
                closeButton.addEventListener('click', () => {
                    const collapseElement = document.getElementById(`collapse${docNum}`);
                    const headingElement = document.getElementById(`heading${docNum}`);
                    if (collapseElement) {
                        collapseElement.parentNode.removeChild(collapseElement);
                    }
                    if (headingElement) {
                        headingElement.parentNode.removeChild(headingElement);
                    }
                });
            }
        }
    }

    /** 
     * Binds the pdf diplay event on click for all new view buttons
     * @param {number} newDocs - The number of new view buttons to configure.
     * @param {number} numberOfDocumentsBefore - Previous number of documents.
     */
    function setupViewEventListener(newDocs, numberOfDocumentsBefore) {
        for (let docNum = numberOfDocumentsBefore+1; docNum <= numberOfDocumentsBefore+newDocs; docNum++) {
            const viewButton = document.getElementById(`view${docNum}`);
            if (viewButton) {
                displayPDF(viewButton.getAttribute('data-document-name'), viewButton.getAttribute('data-page-number'), docNum);
                const viewContainer = document.getElementById(`pdf-${docNum}`);
                viewButton.addEventListener('click', () => {
                    viewContainer.classList.toggle('hide');
                });
            }
        }
    }

    /** 
     * Assigns the pdf to the right button to allow user to display it
     * Add event listener to all the buttons associated to the pdf
     * @param {string} documentName - Name of the document
     * @param {number} pageNumber - Page number where the chunk is located
     * @param {number} viewNumber - Number of the element on the webpage
     */
    async function displayPDF(documentName, pageNumber, viewNumber) {
        const documentData = await getDocument(documentName);
        if (documentData && documentData.url) {
            var url = documentData.url;
            var pdfjsLib = window['pdfjs-dist/build/pdf'];
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.worker.min.js';

            let pdfDoc = null,
                pageNum = parseInt(pageNumber) || 1,
                pageCount = 0,
                scale = 0.9;

            const canvas = document.getElementById(`pdf-canvas-${viewNumber}`);
            var context = canvas.getContext('2d');
            const pageSpan = document.getElementById(`page-info-${viewNumber}`);

            function renderPage(num) {
                pdfDoc.getPage(num).then(function (page) {
                    const viewport = page.getViewport({ scale: scale });
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;

                    const renderContext = {
                        canvasContext: context,
                        viewport: viewport
                    };

                    pageSpan.innerHTML = '';
                    pageSpan.textContent = `${num}/${pageCount}`;

                    page.render(renderContext).promise.then(function () {              
                    });
                });
            }

            pdfjsLib.getDocument(url).promise.then(function(pdfDoc_) {
                // TODO fix the page system, the one Antonin converted are wrong and need pageNumber+1
                pdfDoc = pdfDoc_;
                pageCount = pdfDoc.numPages;
                renderPage(pageNum)
            }, function(reason) {
                console.error(reason);
            });

            function queueRenderPage(num) {
                if (num <= pageCount && num >= 1) {
                    pageNum = num;
                    renderPage(pageNum);
                }
            }

            const prevPageBtn = document.getElementById(`prev-page-${viewNumber}`);
            if (prevPageBtn) {
                prevPageBtn.addEventListener('click', () => {
                    if (pageNum <= 1) return;
                    queueRenderPage(pageNum - 1);
                });
            }

            const nextPageBtn = document.getElementById(`next-page-${viewNumber}`);
            if (nextPageBtn) {
                nextPageBtn.addEventListener('click', () => {
                    if (pageNum >= pageCount) return;
                    queueRenderPage(pageNum + 1);
                });
            }

            const zoomInBtn = document.getElementById(`zoom-in-${viewNumber}`);
            if (zoomInBtn) {
                zoomInBtn.addEventListener('click', () => {
                    scale += 0.1;
                    renderPage(pageNum);
                });
            }

            const zoomOutBtn = document.getElementById(`zoom-out-${viewNumber}`);
            if (zoomOutBtn) {
                zoomOutBtn.addEventListener('click', () => {
                    if (scale <= 0.2) return;
                    scale -= 0.1;
                    renderPage(pageNum);
                });
            }
        }
    }

    /**
     * Submits the user's query from the chat input and handles the response.
     */
    function submitQuery() {
        const userMessage = chatInput.value.trim();
        chatBox.appendChild(createChatMessageElement(userMessage, "outcoming"));
        fetch(`${root}/get`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ msg: userMessage })
        }).then(response => response.json())
        .then(data => {
            chatBox.appendChild(createChatMessageElement(data.response, "incoming"));
            chatBox.scrollTo(0, chatBox.scrollHeight);

            addSearchNumberElement();
            newDocs = data.context.length;


            for (let i = 0; i < newDocs; i++) {
                addContextElement(data.context[i].replace(/\n/g, "<br>"), data.metadatas[i], storedChunks + i + 1);
            }

            waitForNewContextElementsToLoad(newDocs, storedChunks, () => {
                setupContextCollapseEvents(newDocs, storedChunks);
                setupCloseEventListener(newDocs, storedChunks);
                setupViewEventListener(newDocs, storedChunks);
                storedChunks += newDocs
            });
        });
        chatInput.value = "";
        chatInput.style.height = 'auto';
    }

    /**
     * Fetches the list of documents from the server and displays them.
     */
    async function loadDocuments() {
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

    /**
     * Fetches the data for a specific document by its name.
     * @param {string} documentName - The name of the document to fetch.
     * @returns {Promise<Object>} - The fetched document data.
     */
    async function getDocument(documentName) {
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

    /**
     * Toggles the visibility of a sidebar (left or right).
     * @param {string} side - The side of the sidebar to toggle ('left' or 'right').
     */
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

    /**
     * Adjusts the height of the textarea based on its content.
     * @param {Event} event - The input event.
     */
    function adjustTextareaHeight(event) {
        const textarea = event.target;
        textarea.style.height = 'auto';
        textarea.style.height = `${textarea.scrollHeight}px`;
        const maxHeight = parseFloat(window.getComputedStyle(textarea).maxHeight);
        if (textarea.scrollHeight > maxHeight) {
            textarea.style.height = `${maxHeight}px`;
        }
    }

    /**
     * Creates a new chat message list item element.
     * @param {string} message - The message content.
     * @param {string} className - The class name to apply to the list item.
     * @returns {HTMLElement} - The created list item element.
     */
    function createChatMessageElement(message, className) {
        const chatLi = document.createElement("li");
        chatLi.classList.add("message", className);
        chatLi.innerHTML = message;
        return chatLi;
    }

    /**
     * Creates and displays a new context element in the right sidebar.
     * @param {string} context - The context content.
     * @param {string} metadatas - The metadatas of the chunk.
     * @param {number} contextNumber - The numerical identifier for the context.
     */
    async function addContextElement(context, metadatas, contextNumber) {
        let fileName = metadatas["file_name"];

        const cardHeader = document.createElement('div');
        cardHeader.className = 'card-header';
        cardHeader.id = `heading${contextNumber}`;

        const span = document.createElement('span');
        span.className = 'float-start mx-2';

        const cardFooter = document.createElement('div');
        cardFooter.className = 'card-footer text-white';

        const closeButton = document.createElement('button');
        const closeIcon = document.createElement('img');
        closeIcon.classList.add('icon');
        closeIcon.classList.add('download-icon');
        closeIcon.src = `${root}/static/img/cancel.svg`;
        closeButton.id = `close${contextNumber}`;
        closeButton.className = 'btn-ctx-nav';
        closeButton.appendChild(closeIcon);

        const pdfdiv = document.createElement('div');
        pdfdiv.className = 'pdf-viewer hide';
        pdfdiv.id = `pdf-${contextNumber}`;
        const canva = document.createElement('canvas');
        canva.id = `pdf-canvas-${contextNumber}`;

        const doc = await getDocument(fileName);
        if (doc) {
            const docIcon = createIcon(doc);
            span.appendChild(docIcon);
            span.appendChild(document.createTextNode(fileName));

            const downloadButton = document.createElement('button');
            downloadButton.className = 'btn-ctx-nav';
            const downloadLink = createLink(doc);
            downloadLink.textContent = "";

            const downloadIcon = document.createElement('img');
            downloadIcon.classList.add('icon');
            downloadIcon.classList.add('download-icon');
            downloadIcon.src = `${root}/static/img/download.svg`;
    
            downloadLink.appendChild(downloadIcon);
            downloadButton.appendChild(downloadLink);
            cardHeader.appendChild(downloadButton);

            cardFooter.appendChild(downloadButton);
            if(doc.extension.toLowerCase() === 'pdf'){
                const viewButton = document.createElement('button');
                const viewIcon = document.createElement('img');
                viewIcon.classList.add('icon');
                viewIcon.classList.add('download-icon');
                viewIcon.src = `${root}/static/img/view.svg`;
                viewButton.id = `view${contextNumber}`;
                viewButton.className = 'btn-ctx-nav';
                viewButton.setAttribute('data-document-name', fileName);
                viewButton.setAttribute('data-page-number', metadatas["page"]);

                viewButton.appendChild(viewIcon);
                cardFooter.appendChild(viewButton);

                const pdfBtnDiv = document.createElement('div');
                pdfBtnDiv.className = 'pdf-buttons-container';
                const changePageBtnDiv = document.createElement('div');
                changePageBtnDiv.className = 'page-buttons-container';
                const zoomBtnDiv = document.createElement('div');
                zoomBtnDiv.className = 'zoom-buttons-container';

                const prevButton = document.createElement('button');
                const prevIcon = document.createElement('img');
                prevIcon.className = 'icon-pdf';
                prevIcon.src = `${root}/static/img/square-arrow-left.svg`;
                prevButton.id = `prev-page-${contextNumber}`;
                prevButton.className = 'btn';
                prevButton.appendChild(prevIcon);

                const pageInfo = document.createElement('span');
                pageInfo.id = `page-info-${contextNumber}`;
                pageInfo.className = 'page-span';

                const nextButton = document.createElement('button');
                const nextIcon = document.createElement('img');
                nextIcon.className = 'icon-pdf';
                nextIcon.src = `${root}/static/img/square-arrow-right.svg`;
                nextButton.id = `next-page-${contextNumber}`;
                nextButton.className = 'btn';
                nextButton.appendChild(nextIcon);

                const zoomOutButton = document.createElement('button');
                const zoomOutIcon = document.createElement('img');
                zoomOutIcon.className = 'icon-pdf';
                zoomOutIcon.src = `${root}/static/img/search-minus.svg`;
                zoomOutButton.id = `zoom-out-${contextNumber}`;
                zoomOutButton.className = 'btn';
                zoomOutButton.appendChild(zoomOutIcon);

                const zoomInButton = document.createElement('button');
                const zoomInIcon = document.createElement('img');
                zoomInIcon.className = 'icon-pdf';
                zoomInIcon.src = `${root}/static/img/search-add.svg`;
                zoomInButton.id = `zoom-in-${contextNumber}`;
                zoomInButton.className = 'btn';
                zoomInButton.appendChild(zoomInIcon);

                const fullscreenButton = document.createElement('button');
                fullscreenButton.textContent = 'Full screen';
                fullscreenButton.id = `fullscreen-${contextNumber}`;
                fullscreenButton.className = 'btn';

                // Append buttons to cardFooter
                cardFooter.appendChild(viewButton);
                changePageBtnDiv.appendChild(prevButton);
                changePageBtnDiv.appendChild(pageInfo);
                changePageBtnDiv.appendChild(nextButton);
                zoomBtnDiv.appendChild(zoomOutButton);
                zoomBtnDiv.appendChild(zoomInButton);
                //cardFooter.appendChild(fullscreenButton);
                pdfBtnDiv.appendChild(changePageBtnDiv);
                pdfBtnDiv.appendChild(zoomBtnDiv);
                pdfdiv.appendChild(pdfBtnDiv);
            }           
            cardFooter.appendChild(closeButton);

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

        cardBody.appendChild(cardFooter);

        pdfdiv.appendChild(canva);
        cardBody.appendChild(pdfdiv);

        collapseDiv.appendChild(cardBody);

        const container = document.querySelector('.context-retriever');
        container.appendChild(cardHeader);
        container.appendChild(collapseDiv);
    }

    /**
     * Adds an element indicating the search number in the right sidebar.
     */
    function addSearchNumberElement() {
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

    /**
     * Clears the chat history and optionally resets the interface on load.
     * @param {boolean} [onLoad=false] - If true, resets the interface on page load.
     */
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

    /**
     * Waits for all context elements to load before executing a callback.
     * @param {number} newDocs - The number of new context documents to wait for.
     * @param {number} numberOfDocumentsBefore - Previous number of documents.
     * @param {Function} callback - The callback function to execute after elements are loaded.
     */
    function waitForNewContextElementsToLoad(newDocs, numberOfDocumentsBefore, callback) {
        const interval = setInterval(() => {
            let allExist = true;
            for (let i = numberOfDocumentsBefore+1; i <= numberOfDocumentsBefore+newDocs; i++) {
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

    /**
     * Creates an icon element representing the document type.
     * @param {Object} doc - The document object containing its details.
     * @returns {HTMLElement} - The created icon element.
     */
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

    /**
     * Creates a download link element for a document.
     * @param {Object} doc - The document object containing its details.
     * @returns {HTMLElement} - The created link element.
     */
    function createLink(doc) {
        const link = document.createElement('a');
        link.href = doc.url;
        link.textContent = doc.name;
        link.title = doc.name;
        link.target = "_blank";
        return link;
    }

    /**
     * Handles changes in the visibility state of the document.
     */
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

    /**
     * Handles responsive class changes based on window width.
     */
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

    /**
     * Hides the overlay element after a delay.
     */
    function hideOverlay() {
        const overlay = document.getElementById("overlay");
        setTimeout(() => {
            overlay.classList.add("hidden");
        }, 500);
    }

    /**
     * Configures options related to the RAG (Retriever-Augmented Generation) settings.
     */
    function configureRagOptions() {
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

    // Initialize the script
    window.onload = function() {
        init();
    };
});
