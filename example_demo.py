"""
Example demonstration of the Memory Agent showcasing long-term memory capabilities.
This script shows how the agent remembers user preferences and past conversations.
"""

from main import MemoryAgent


def demo_conversation():
    """Demonstrate the memory agent with a sample conversation sequence"""
    print("=== Memory Agent Long-Term Memory Demo ===\n")
    
    agent = MemoryAgent()
    graph = agent.create_graph()
    
    # User ID for consistent memory across sessions
    user_id = "demo_user_123"
    
    # Sample conversation sequence demonstrating memory
    conversation_scenarios = [
        {
            "title": "Initial Introduction",
            "messages": [
                "Hi, my name is Alice and I'm a software developer from San Francisco.",
                "I love working with Python and machine learning projects.",
                "My favorite programming framework is Django for web development."
            ]
        },
        {
            "title": "Personal Preferences",
            "messages": [
                "I prefer working in the mornings, usually starting at 7 AM.",
                "I'm vegetarian and love Italian cuisine.",
                "My hobby is playing chess on weekends."
            ]
        },
        {
            "title": "Memory Recall Test",
            "messages": [
                "What do you remember about me?",
                "What's my preferred work schedule?",
                "What kind of food do I like?"
            ]
        }
    ]
    
    # Run through scenarios
    for scenario in conversation_scenarios:
        print(f"\n--- {scenario['title']} ---")
        
        for message in scenario['messages']:
            print(f"\nYou: {message}")
            
            # Process the message through the agent
            result = graph.invoke({
                "messages": [{"role": "user", "content": message}],
                "user_id": user_id
            })
            
            # Display the response
            if result["messages"]:
                assistant_response = result['messages'][-1].content
                print(f"Assistant: {assistant_response}")
        
        input("\nPress Enter to continue to next scenario...")
    
    print("\n=== Demo Complete ===")
    print("The agent should now have persistent memories about Alice.")
    print("You can continue the conversation to see how it references past interactions.")


def interactive_session():
    """Run an interactive session with the memory agent"""
    print("\n=== Interactive Memory Agent Session ===")
    print("Type 'quit' to exit, 'demo' to run the demo scenario\n")
    
    agent = MemoryAgent()
    graph = agent.create_graph()
    
    user_id = input("Enter your user ID (or press Enter for 'demo_user'): ").strip()
    if not user_id:
        user_id = "demo_user"
    
    print(f"Starting session for user: {user_id}")
    print("The agent will remember our conversation for future sessions.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() == 'quit':
                break
            elif user_input.lower() == 'demo':
                demo_conversation()
                continue
            
            # Basic input validation
            if not user_input:
                print("Please enter a message.")
                continue
                
            if len(user_input) > 10000:
                print("Message too long. Please keep messages under 10,000 characters.")
                continue
                
            # Process the message
            result = graph.invoke({
                "messages": [{"role": "user", "content": user_input}],
                "user_id": user_id
            })
            
            # Display response
            if result["messages"]:
                print(f"Assistant: {result['messages'][-1].content}\n")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print("An unexpected error occurred. Please try again.")
            continue


if __name__ == "__main__":
    print("Memory Agent Demo Options:")
    print("1. Run automated demo scenario")
    print("2. Interactive session")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == "1":
            demo_conversation()
            break
        elif choice == "2":
            interactive_session()
            break
        else:
            if not choice:
                print("Please enter a choice.")
            else:
                print(f"Invalid choice '{choice}'. Please enter 1 or 2.")