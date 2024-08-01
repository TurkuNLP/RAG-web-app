import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline
)

from langchain_community.llms import HuggingFacePipeline

from parameters import LLM_MODEL

global_model = None


def get_llm_function(model_name = LLM_MODEL):
    """get LLM model between :
    - mistralai/Mixtral-8x7B-Instruct-v0.1
    - mistralai/Mistral-7B-Instruct-v0.1
    - nvidia/Llama3-ChatQA-1.5-8B
    - gpt-3.5-turbo
    Other models can of course be implemented later"""

    global global_model
    if (model_name == "mistralai/Mixtral-8x7B-Instruct-v0.1" or model_name == "mistralai/Mistral-7B-Instruct-v0.1"):
        if global_model is None:
            tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, token=HF_API_TOKEN)
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.padding_side = "right"

            #################################################################
            # bitsandbytes parameters
            #################################################################

            # Activate 4-bit precision base model loading
            use_4bit = True
            
            # Compute dtype for 4-bit base models
            bnb_4bit_compute_dtype = "float16"
            
            # Quantization type (fp4 or nf4)
            bnb_4bit_quant_type = "nf4"
            
            # Activate nested quantization for 4-bit base models (double quantization)
            use_nested_quant = False
            
            #################################################################
            # Set up quantization config
            #################################################################
            compute_dtype = getattr(torch, bnb_4bit_compute_dtype)
            
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=use_4bit,
                bnb_4bit_quant_type=bnb_4bit_quant_type,
                bnb_4bit_compute_dtype=compute_dtype,
                bnb_4bit_use_double_quant=use_nested_quant,
            )
            
            # Check GPU compatibility with bfloat16
            
            if compute_dtype == torch.float16 and use_4bit:
                major, _ = torch.cuda.get_device_capability()
                if major >= 8:
                    print("=" * 80)
                    print("Your GPU supports bfloat16: accelerate training with bf16=True")
                    print("=" * 80)

            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                token = HF_API_TOKEN,
                #quantization_config = bnb_config
            )

            text_generation_pipeline = pipeline(
                model=model,
                tokenizer=tokenizer,
                task="text-generation",
                temperature=0.2,
                repetition_penalty=1.1,
                return_full_text=True,
                max_new_tokens=1000,
            )
            
            global_model = HuggingFacePipeline(pipeline=text_generation_pipeline)
        
        return global_model
    
    elif model_name == "nvidia/Llama3-ChatQA-1.5-8B":
        if global_model is None:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16, device_map="auto")
            text_generation_pipeline = pipeline(
                model=model,
                tokenizer=tokenizer,
                task="text-generation",
                temperature=0.2,
                repetition_penalty=1.1,
                return_full_text=True,
                max_new_tokens=1000,
            )
            global_model = HuggingFacePipeline(pipeline=text_generation_pipeline)
        return global_model

    elif model_name == "gpt-3.5-turbo":
        from langchain_openai import ChatOpenAI
        model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
        return model
    
    else:
        print(f'Model "{model_name}" is not implemented on the system.')
        return