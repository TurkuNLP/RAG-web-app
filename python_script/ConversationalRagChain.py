from langchain.chains.base import Chain
from langchain.output_parsers import YamlOutputParser
from typing import List, Dict, Any, Optional
from langchain.callbacks.manager import CallbackManagerForChainRun, Callbacks
from langchain.llms.base import BaseLanguageModel
from pydantic import BaseModel
from langdetect import detect
from deep_translator import GoogleTranslator

from langchain_core.runnables import RunnableBinding

from parameters import REPHRASING_PROMPT, STANDALONE_PROMPT, ROUTER_DECISION_PROMPT

class ResultYAML(BaseModel):
    result: bool


class ConversationalRagChain(Chain):
    """Chain that encpsulate RAG application enablingnatural conversations"""
    rag_chain: RunnableBinding
    yaml_output_parser: YamlOutputParser
    llm: BaseLanguageModel
    
    # input\output parameters
    input_key: str = "query"
    output_key: str = "result"
    context_key: str = "context"
    translate_key: str = "translate"
    metadatas_key: str = "metadatas"

    chat_history = []
    
    @property
    def input_keys(self) -> List[str]:
        """Input keys."""
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Output keys."""
        return [self.output_key, self.context_key, self.metadatas_key]

    @property
    def _chain_type(self) -> str:
        """Return the chain type."""
        return "ConversationalRagChain"

    @classmethod
    def from_llm(
            cls,
            rag_chain: RunnableBinding,
            llm: BaseLanguageModel,
            callbacks: Callbacks = None,
            **kwargs: Any,
    ) -> 'ConversationalRagChain':
        """Initialize from LLM."""

        return cls(
            llm=llm,
            rag_chain=rag_chain,
            yaml_output_parser=YamlOutputParser(pydantic_object=ResultYAML),
            callbacks=callbacks,
            **kwargs,
        )

    def format_standalone_response(self, response) -> str:
        """Removes the prompt from the generated response"""

        end_marker = "<|endofprompt|>"
        marker_index = response.find(end_marker)
        if marker_index != -1:
            response = response[marker_index + len(end_marker):].strip()
        return response

    def translate_with_llm(self, text: str, target_language: str = "English") -> str:
        """Use the LangChain model to translate text."""

        prompt = f"Translate the following text to {target_language}:\n\n{text}"
        translation = self.llm(prompt)
        return translation
    
    @staticmethod
    def translate_text(text: str, max_chars: int = 5000) -> str:
        """Translate text from Russian to English in chunks if it exceeds max_chars."""
        translator = GoogleTranslator(source="ru", target="en")
        
        # If text is within limit, translate directly
        if len(text) <= max_chars:
            return translator.translate(text)
        
        # Otherwise, split the text into chunks and translate each chunk
        translated_chunks = []
        for i in range(0, len(text), max_chars):
            chunk = text[i:i + max_chars]
            translated_chunks.append(translator.translate(chunk))
        
        # Combine translated chunks
        return ' '.join(translated_chunks)

    def format_outputs(self, output: Dict[str, Any]):
        """Removes the prompt from the generated response
        Regroups the contexts and metadatas of different documents in dedicated lists."""

        answer = output["answer"]
        AI_marker = "Assistant: "
        marker_index = answer.find(AI_marker)
        if marker_index != -1:
            answer = answer[marker_index + len(AI_marker):].strip()
        else:
            AI_marker = "AI: "
            marker_index = answer.find(AI_marker)
            if marker_index != -1:
                answer = answer[marker_index + len(AI_marker):].strip()
            
        documents = output['context']
        contexts = []
        translates = []
        metadatas = []
        for doc in documents:
            contexts.append(doc.page_content)
            detected_lang = detect(doc.page_content)

            # Translate using the LangChain model if not in English
            if detected_lang != "en":
                translates.append(self.translate_text(doc.page_content))
            try:
                metadatas.append(doc.metadata)
            except:
                # TODO Update database which has the last metadata storage system
                # TODO Delete this section when alla databases will be updated
                print("Conflict version between new and last metadata storage in the database")
                print("You have to update the database")
        return answer, contexts, translates, metadatas

    def update_chat_history(self, user_question, bot_response):
        """Update the chat history"""
        self.chat_history.append({"role": "user", "content": user_question})
        self.chat_history.append({"role": "ai", "content": bot_response})

    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_history = []

    def _call(self, inputs: Dict[str, Any], run_manager: Optional[CallbackManagerForChainRun] = None) -> Dict[str, Any]:
        """Call the chain. Return a dict with answer, context and metadatas"""
        chat_history = self.chat_history
        question = inputs[self.input_key]

        output = self.rag_chain.invoke({"input": question, "chat_history": chat_history})
        answer, contexts, translates, metadatas = self.format_outputs(output)

        if not contexts:
            answer = "No context found, try rephrasing your question"
            
        self.update_chat_history(question, answer) 
        return {self.output_key: answer, self.context_key: contexts, self.translate_key:translates, self.metadatas_key: metadatas}