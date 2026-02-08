try:
    import torch
    from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("WARNING: Transformers not found. Running LLM in Mock Mode.")

class HistoricalLLM:
    def __init__(self, model_path: str = None, device: str = "cpu"):
        """
        Initialize the LLM.
        """
        self.model_path = model_path
        self.pipeline = None
        self.load_error = None  # Track errors
        self.config = {
            "max_new_tokens": 150,
            "temperature": 0.1,  
            "do_sample": True
        }

        if ML_AVAILABLE and model_path and (model_path != "mock"):
            try:
                print(f"Loading local model from {model_path}...")
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModelForCausalLM.from_pretrained(model_path)
                self.pipeline = pipeline(
                    "text-generation", 
                    model=self.model, 
                    tokenizer=self.tokenizer,
                    device=-1 if device=="cpu" else 0
                )
            except Exception as e:
                print(f"Failed to load model from {model_path}: {e}")
                self.load_error = str(e)
                self.pipeline = None
        else:
            if model_path != "mock" and not ML_AVAILABLE:
                pass # Already printed warning
            elif model_path != "mock":
                 print("No model path provided or mock requested. Using Mock LLM.")

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if self.pipeline:
            # Real offline inference
            
            # Check if model supports chat templates (TinyLlama, Mistral, etc.)
            if hasattr(self.tokenizer, "chat_template") and self.tokenizer.chat_template:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
                # Apply template but do NOT add generation prompt yet if pipeline handles it, 
                # strictly speaking pipeline(text-generation) expects string.
                # tokenize=False ensures we get a string back.
                full_prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            else:
                # Fallback for GPT-2 (Raw concat)
                full_prompt = f"{system_prompt}\n\n{user_prompt}"

            # Added repetition penalty to reduce loops
            outputs = self.pipeline(full_prompt, **self.config, repetition_penalty=1.2)
            generated_text = outputs[0]['generated_text']
            
            # Smart cleanup: remove the prompt from the output
            if generated_text.startswith(full_prompt):
                return generated_text[len(full_prompt):].strip()
            return generated_text
        else:
            # Mock reasoning for demonstration
            # Extract the actual question from the prompt more robustly
            try:
                # expecting "Question:\n{query}\n\nAnswer..."
                question_part = user_prompt.split("Question:")[-1].split("Answer")[0].strip()
            except:
                question_part = "the unknown"

            # Extended knowledge base for Mock Mode
            lower_q = question_part.lower()
            if "newton" in lower_q:
                return "Sir Isaac Newton (1642–1727) was an English mathematician, physicist, astronomer, alchemist, theologian, and author. He is best known for his laws of motion and universal gravitation."
            elif "evolution" in lower_q or "darwin" in lower_q:
                return "Charles Darwin propounded the theory of evolution by natural selection, detailing how species adapt over time in his seminal work 'On the Origin of Species' (1859)."
            elif "lincoln" in lower_q:
                return "Abraham Lincoln served as the 16th President of the United States, leading the nation through its Civil War and issuing the Emancipation Proclamation."
            elif "electron" in lower_q:
                return "The electron was recently identified by J.J. Thomson in 1897 as a corpuscle of negative charge, revolutionizing our understanding of atomic structure."
            elif "electricity" in lower_q:
                return "Electricity is a set of physical phenomena associated with the presence and motion of matter that has a property of electric charge. It is harnessed today for telegraphy, lighting, and industrial motors."
            elif "light" in lower_q:
                return "Light is understood to be a transverse electromagnetic wave, as described by James Clerk Maxwell's equations. Its speed has been measured with great precision by Michelson."
            
            # Generic valid fallback for anything else (instead of error message)
            return f"Regarding '{question_part}', the archives contain references to this subject in the context of late 19th-century thought. While specific details are retrieving... scholars of this era generally regard it as a significant field of natural philosophy and history."

