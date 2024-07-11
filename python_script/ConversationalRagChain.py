from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.output_parsers import YamlOutputParser
from langchain_core.messages import HumanMessage
from typing import List, Dict, Any, Optional
from langchain.callbacks.manager import CallbackManagerForChainRun, Callbacks
from langchain.llms.base import BaseLanguageModel
from pydantic import BaseModel

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

    def format_standalone_response(self, response):
        """Removes the prompt from the generated response"""

        end_marker = "<|endofprompt|>"
        marker_index = response.find(end_marker)
        if marker_index != -1:
            response = response[marker_index + len(end_marker):].strip()
        return response

    def format_outputs(self, output: Dict[str, Any]):
        """Removes the prompt from the generated response
        Regroups the contexts and sources of different documents in dedicated lists."""

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
        sources = []
        for doc in documents:
            contexts.append(doc.page_content)
            sources.append(doc.metadata['source'])
        return answer,contexts,sources

    def update_chat_history(self, user_question, bot_response):
        """Update the chat history"""
        self.chat_history.append({"role": "user", "content": user_question})
        self.chat_history.append({"role": "ai", "content": bot_response})

    def clear_chat_history(self):
        """Clear chat history"""
        self.chat_history = []

    def _call(self, inputs: Dict[str, Any], run_manager: Optional[CallbackManagerForChainRun] = None) -> Dict[str, Any]:
        """Call the chain. Return a dict with answer, context and source"""
        chat_history = self.chat_history
        print(chat_history)
        question = inputs[self.input_key]

        output = self.rag_chain.invoke({"input": question, "chat_history": chat_history})
        answer,contexts,sources = self.format_outputs(output)

        self.update_chat_history(question, answer) 
        return {self.output_key: answer, self.context_key: contexts, self.source_key: sources}