from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.output_parsers import YamlOutputParser
from typing import List, Dict, Any, Optional
from langchain.callbacks.manager import CallbackManagerForChainRun, Callbacks
from langchain.llms.base import BaseLanguageModel
from pydantic import BaseModel

from parameters import REPHRASING_PROMPT, STANDALONE_PROMPT, ROUTER_DECISION_PROMPT

class ResultYAML(BaseModel):
    result: bool


class ConversationalRagChain(Chain):
    """Chain that encpsulate RAG application enablingnatural conversations"""
    rag_chain: Chain
    rephrasing_chain: LLMChain
    standalone_question_chain: LLMChain
    router_decision_chain: LLMChain
    yaml_output_parser: YamlOutputParser
    llm: BaseLanguageModel
    
    # input\output parameters
    input_key: str = "query"
    output_key: str = "result"
    context_key: str = "context"
    source_key: str = "source"

    chat_history = []
    
    @property
    def input_keys(self) -> List[str]:
        """Input keys."""
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Output keys."""
        return [self.output_key, self.context_key, self.source_key]

    @property
    def _chain_type(self) -> str:
        """Return the chain type."""
        return "ConversationalRagChain"

    @classmethod
    def from_llm(
            cls,
            rag_chain: Chain,
            llm: BaseLanguageModel,
            callbacks: Callbacks = None,
            **kwargs: Any,
    ) -> 'ConversationalRagChain':
        """Initialize from LLM."""
    
        # create the rephrasing chain
        rephrasing_chain = LLMChain(llm=llm, prompt=REPHRASING_PROMPT, callbacks=callbacks)
    
        # create the standalone question chain
        standalone_question_chain = LLMChain(llm=llm, prompt=STANDALONE_PROMPT, callbacks=callbacks)
    
        # router decision chain
        router_decision_chain = LLMChain(llm=llm, prompt=ROUTER_DECISION_PROMPT, callbacks=callbacks)
    
        return cls(
            llm=llm,
            rag_chain=rag_chain,
            rephrasing_chain=rephrasing_chain,
            standalone_question_chain=standalone_question_chain,
            router_decision_chain=router_decision_chain,
            yaml_output_parser=YamlOutputParser(pydantic_object=ResultYAML),
            callbacks=callbacks,
            **kwargs,
        )

    def format_standalone_response(self, response):
        """Removes the prompt from the generated response"""

        end_marker = "<|endofprompt|>"
        marker_index = response.find(end_marker)
        if marker_index != -1:
            response = response[marker_index + len(end_marker):].strip()
        return response

    def format_outputs(self, response: Dict[str, Any]):
        """Removes the prompt from the generated response
        Regroups the contexts and sources of different documents in dedicated lists."""

        end_marker = "<|endofprompt|>"
        answer = response['result']
        marker_index = answer.find(end_marker)
        if marker_index != -1:
            answer = answer[marker_index + len(end_marker):].strip()
        documents = response['source_documents']
        contexts = []
        sources = []
        for doc in documents:
            contexts.append(doc.page_content)
            sources.append(doc.metadata['id'])
        return answer,contexts,sources

    def update_chat_history(self, user_question, bot_response):
        """Update the chat history"""
        self.chat_history.append({"role": "user", "content": user_question})
        self.chat_history.append({"role": "ai", "content": bot_response})

    def _call(self, inputs: Dict[str, Any], run_manager: Optional[CallbackManagerForChainRun] = None) -> Dict[str, Any]:
        """Call the chain. Return a dict with answer, context and source"""
        chat_history = self.chat_history
        question = inputs[self.input_key]
        
        if not chat_history:
            answer = self.rag_chain.invoke({"query": question})
            answer, contexts, sources = self.format_outputs(answer)
            self.update_chat_history(question, answer)
            return {self.output_key: answer, self.context_key: contexts, self.source_key: sources}
        """
        needs_rephrasing = self.rephrasing_chain.invoke({"chat_history": chat_history, "question": question})['text'].strip()
        rephrasing_decision = self.yaml_output_parser.parse(needs_rephrasing)
        print(rephrasing_decision)
        
        if rephrasing_decision.result:
            print("rephrasing")
        """
        question = self.standalone_question_chain.invoke({"chat_history": chat_history, "question": question})['text'].strip()
        question = self.format_standalone_response(question)
        answer = self.rag_chain.invoke({"query": question})
        answer, contexts, sources = self.format_outputs(answer)
        self.update_chat_history(question, answer) 
        return {self.output_key: answer, self.context_key: contexts, self.source_key: sources}