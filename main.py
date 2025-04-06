import os
from dotenv import load_dotenv
from typing import List, Annotated, TypedDict
import logging
import uuid
import datetime  # For timestamping the conversation file

# Load environment variables from .env file
load_dotenv()

# Check if the Google API Key is set
if not os.environ.get("GOOGLE_API_KEY"):
    print("Error: GOOGLE_API_KEY not found in environment variables or .env file.")
    print("Please create a .env file in the root directory with the following content:")
    print("GOOGLE_API_KEY=YOUR_API_KEY_HERE")
    # Optionally exit if the key is critical
    # exit(1) 
else:
    print("GOOGLE_API_KEY loaded successfully.")

print("Environment setup complete.")

# Define the directory where your Arabic TXT files are located
txt_dir_arabic = "./content_arabic"

if not os.path.isdir(txt_dir_arabic):
    print(f"Error: Directory '{txt_dir_arabic}' not found.")
    print("Please make sure the directory exists and contains your Arabic .txt files.")
    all_docs_text = ""
else:
    print(f"Directory '{txt_dir_arabic}' found. Proceeding to load files.")
    all_docs_text = None

from langchain_community.document_loaders import DirectoryLoader, TextLoader

# Initialize all_docs_text if the directory check passed but it wasn't set
if all_docs_text is None:
    all_docs_text = ""

# Proceed only if the directory exists
if os.path.isdir(txt_dir_arabic):
    try:
        print(f"Loading TXT files from: {txt_dir_arabic}")
        # Use DirectoryLoader with TextLoader for .txt files, specifying UTF-8 encoding
        loader = DirectoryLoader(
            txt_dir_arabic,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={'encoding': 'utf-8'},
            show_progress=True,
            use_multithreading=True
        )
        docs = loader.load()

        if not docs:
            print(f"Warning: No .txt documents found in '{txt_dir_arabic}'. The chatbot will not have any context.")
            all_docs_text = ""
        else:
            all_docs_text = "\n\n--- FILE SEPARATOR ---\n\n".join([doc.page_content for doc in docs])
            print(f"Successfully loaded and combined content from {len(docs)} .txt document(s).")

    except Exception as e:
        logging.error(f"Error loading TXT files from {txt_dir_arabic}: {e}", exc_info=True)
        print(f"An error occurred while loading text files. Please check the files and directory. Error: {e}")
        all_docs_text = ""

# Final check if we loaded any text
if not all_docs_text:
    print("\nWarning: No text content loaded from files. The chatbot context will be empty.")

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0, convert_system_message_to_human=True)
    print("Using Gemini 1.5 Pro model.")
except Exception as e:
    print(f"Error initializing Gemini model: {e}")
    llm = None

def generate_answer(state: ChatState):
    print("---NODE: GENERATE ANSWER---")
    if llm is None:
         return {"messages": [AIMessage(content="Model not initialized.")]}
    if not all_docs_text:
         print("---CONTEXT: No document content loaded.---")
         return {"messages": [AIMessage(content="لا يمكنني الإجابة على هذا السؤال لعدم توفر محتوى المستندات النصية.")]}

    current_messages = state['messages']
    if not current_messages:
        print("---ERROR: No messages found in state.---")
        return {"messages": [AIMessage(content="An internal error occurred (no messages).")]}
    last_question = current_messages[-1].content

    '''
    For branch-related questions (such as address, operating hours, pricing, etc.), only return details if you are sure which branch the patient is asking about. If the branch is unclear from the conversation, politely ask for clarification rather than providing multiple branch details.
    '''
    prompt_template = f"""

You are a clinic AI agent designed to answer patient questions exclusively using the data provided in your context (i.e. the contents of multiple text files). Do not use any pre-existing knowledge outside of the supplied documents.

Your response style must:

Provide detailed, human-like, and friendly answers.

Extract and include all relevant details from the provided documents.

Use transitional words and phrases (linking words, connectors, discourse markers) to create coherence and a smooth flow in your writing.

For multiple queries in one request (e.g., branch address, operating hours, pricing), separate each answer with two line breaks.

When sending the address of a branch, include the branch address followed by two line breaks and then add the location link for that branch.

For inquiries phrased in Arabic using words like "ممكن", begin with a warm, conversational preamble (for example, "اكيد هبعتلك …") and then provide the information after a space in the same message.

**your answers must be in egyptian arabic accent**

For reservation requests:

Identify from the conversation the following required information: branch, day or date of reservation, patient name, and phone number.

Ask politely for any missing details if some of this information is not provided.

Once you have all the required details, send a confirmation message that includes a statement like “تم الحجز بالتفاصيل التالية” (or the equivalent in your tone) followed by the complete reservation details.

Detect the user's gender from the conversation context (if possible) and adjust your tone and phrasing accordingly.

Important:
Answer only with the details extracted from the text files in your context window. Do not add any extra information from your training data or external knowledge.

**سياق من المستندات النصية:**
{all_docs_text}
---
**سجل المحادثة:**
{[f'{m.type}: {m.content}' for m in current_messages[:-1]]}
---
**السؤال:**
{last_question}

**الإجابة بناءً على السياق فقط:**
"""
    try:
        response = llm.invoke([HumanMessage(content=prompt_template)])
        ai_response = response
    except Exception as e:
        print(f"---ERROR during LLM invocation: {e}---")
        logging.error(f"Error during LLM invocation: {e}", exc_info=True)
        ai_response = AIMessage(content="حدث خطأ أثناء محاولة إنشاء الإجابة.")

    return {"messages": [ai_response]}

# Function to save conversation history to file with RTL support
def save_conversation_to_file(conversation_history, filename=None):
    """Save the conversation history to a text file with proper RTL markers for Arabic."""
    if filename is None:
        # Create a filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Add a BOM (Byte Order Mark) to help text editors recognize UTF-8
            f.write('\ufeff')
            
            # Add title and timestamp
            f.write(f"Conversation History - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*50 + "\n\n")
            
            for entry in conversation_history:
                # Add RTL mark (U+200F) for better Arabic text handling
                rtl_mark = '\u200F'
                
                # Write the role and content with RTL mark
                f.write(f"{entry['role']}: {rtl_mark}{entry['content']}\n\n")
        
        print(f"Conversation saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving conversation: {e}")
        return False

# --- 5. Build and Compile the Graph ---
workflow = StateGraph(ChatState)
workflow.add_node("generate_answer", generate_answer)
workflow.add_edge(START, "generate_answer")
workflow.add_edge("generate_answer", END)
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
print("Graph compiled successfully.")

# --- 6. Interactive Chat Loop ---
print("\n--- Starting Chatbot ---")
print("Enter 'quit', 'exit', or 'خروج' to end the chat.")

# Check if LLM and context are ready
if llm is None:
    print("Cannot start chat: LLM not initialized.")
elif not all_docs_text:
    print("Cannot start chat: No document content loaded.")
else:
    current_thread_id = str(uuid.uuid4()) # Start a new conversation thread
    print(f"New conversation started (Thread ID: {current_thread_id})")
    
    # Initialize conversation history
    conversation_history = []

    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["quit", "exit", "خروج"]:
                print("--- Chat Ended ---")
                
                # Save the conversation when exiting
                if conversation_history:
                    save_conversation_to_file(conversation_history)
                break

            if not user_input.strip():
                continue
                
            # Add user message to history
            conversation_history.append({"role": "User", "content": user_input})

            config = {"configurable": {"thread_id": current_thread_id}}
            inputs = {"messages": [HumanMessage(content=user_input)]}

            final_state = None
            print("Assistant: ", end="", flush=True)
            for event in app.stream(inputs, config=config, stream_mode="values"):
                final_state = event # Keep track of the latest state

            # Print the last message which is the AI response
            if final_state and "messages" in final_state and final_state["messages"]:
                ai_response = final_state["messages"][-1].content
                print(ai_response)
                
                # Add AI response to history
                conversation_history.append({"role": "Assistant", "content": ai_response})
            else:
                print("Sorry, I couldn't generate a response.")
                conversation_history.append({"role": "Assistant", "content": "Sorry, I couldn't generate a response."})

        except KeyboardInterrupt:
            print("\n--- Chat Interrupted ---")
            
            # Save the conversation on keyboard interrupt too
            if conversation_history:
                save_conversation_to_file(conversation_history)
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            logging.error(f"Error in chat loop for thread {current_thread_id}: {e}", exc_info=True)
            # Add error to history
            conversation_history.append({"role": "System", "content": f"Error: {e}"})