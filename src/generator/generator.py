"""Generator module for Doc Assist."""

import re

class CodeGenerator:
    """
    Code generator using rule-based approach for the sample data.
    """
    
    def __init__(self, model_name=None, device=None):
        """
        Initialize the generator.
        
        Args:
            model_name: Not used in this implementation
            device: Not used in this implementation
        """
        pass

    def extract_code_from_contexts(self, contexts):
        """
        Extract code snippets from contexts.
        
        Args:
            contexts: List of context documents
            
        Returns:
            List of code snippets
        """
        code_snippets = []
        for ctx in contexts:
            # Check if the context contains code-like patterns
            if any(pattern in ctx for pattern in ["import", "def ", "=", "for ", "if ", "print("]):
                # Extract only the code part if the context has a question
                if "?" in ctx and "\n" in ctx:
                    # Try to get only the code part after the question
                    parts = ctx.split("?", 1)
                    if len(parts) > 1:
                        code_snippets.append(parts[1].strip())
                    else:
                        code_snippets.append(ctx)
                else:
                    code_snippets.append(ctx)
        
        return code_snippets

    def generate(self, query, contexts, max_tokens=200):
        """
        Generate an answer based on the query and contexts.
        
        Args:
            query: User query
            contexts: List of context documents
            max_tokens: Not used in this implementation
            
        Returns:
            Generated answer
        """
        query_lower = query.lower()
        
        # Handle general questions about libraries
        if query_lower.startswith("what is") or query_lower.startswith("tell me about"):
            return self.answer_general_question(query_lower, contexts)
        
        # Extract code snippets from contexts
        code_snippets = self.extract_code_from_contexts(contexts)
        
        # If we found code snippets, use them
        if code_snippets:
            # Find the most relevant code snippet based on the query
            best_snippet = self.find_best_snippet(query, code_snippets)
            
            # Format the answer
            answer = f"To {query.lower().rstrip('?')}, you can use the following code:\n\n```python\n{best_snippet}\n```"
            
            # Add explanation if needed
            if "how" in query_lower and "?" in query:
                answer += "\n\nThis code demonstrates the basic approach. You can modify it according to your specific needs."
            
            return answer
        else:
            # Fallback if no code snippets found
            return f"I don't have specific code examples for '{query}' in my context. Please try a different question."
            
    def answer_general_question(self, query_lower, contexts):
        """
        Answer general questions about libraries.
        
        Args:
            query_lower: Lowercase query
            contexts: List of context documents
            
        Returns:
            Generated answer
        """
        # Library descriptions
        library_info = {
            "numpy": "NumPy is a fundamental package for scientific computing in Python. It provides support for large, multi-dimensional arrays and matrices, along with a large collection of high-level mathematical functions to operate on these arrays. NumPy is widely used in data analysis, machine learning, and scientific computing.",
            "pandas": "Pandas is a powerful data manipulation and analysis library for Python. It provides data structures like DataFrame and Series that are designed for efficient data manipulation with integrated indexing. Pandas is widely used for data cleaning, transformation, and analysis tasks.",
            "matplotlib": "Matplotlib is a comprehensive library for creating static, animated, and interactive visualizations in Python. It provides a MATLAB-like interface for creating plots and graphs.",
            "python": "Python is a high-level, interpreted programming language known for its readability and versatility. It supports multiple programming paradigms including procedural, object-oriented, and functional programming."
        }
        
        # Extract the subject of the question
        subject = None
        for lib in library_info.keys():
            if lib in query_lower:
                subject = lib
                break
        
        if subject:
            # Provide general information about the library
            answer = library_info[subject]
            
            # Add an example if available in contexts
            for ctx in contexts:
                if subject in ctx.lower() and any(pattern in ctx for pattern in ["import", "=", "def"]):
                    answer += f"\n\nHere's a simple example of using {subject}:\n\n```python\n{ctx}\n```"
                    break
            
            return answer
        else:
            return f"I don't have information about this topic in my context. Please try asking about Python, NumPy, or Pandas with more specific questions."

    
    def find_best_snippet(self, query, snippets):
        """
        Find the most relevant code snippet for the query.
        
        Args:
            query: User query
            snippets: List of code snippets
            
        Returns:
            Most relevant code snippet
        """
        # Convert query to lowercase for matching
        query_lower = query.lower()
        
        # Keywords to look for in the query
        keywords = {
            "numpy": ["numpy", "array", "np."],
            "pandas": ["pandas", "dataframe", "csv", "pd.", "groupby"],
            "list": ["list", "array", "sort"],
            "string": ["string", "text", "lowercase", "uppercase"],
            "function": ["function", "def"],
            "loop": ["loop", "iterate", "for"],
            "file": ["file", "read", "write", "open"]
        }
        
        # Score each snippet based on keyword matches
        best_score = -1
        best_snippet = snippets[0] if snippets else ""
        
        for snippet in snippets:
            score = 0
            
            # Check for keyword matches in both query and snippet
            for category, terms in keywords.items():
                for term in terms:
                    if term in query_lower and term in snippet.lower():
                        score += 2
                    elif term in query_lower or term in snippet.lower():
                        score += 1
            
            if score > best_score:
                best_score = score
                best_snippet = snippet
        
        return best_snippet
