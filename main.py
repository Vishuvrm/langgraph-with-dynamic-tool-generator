from src.interface import GraphInterface


def main():
    """Main entry point for the debate application"""
    debate_system = GraphInterface()
    print("\n🧠 Chat Initialized. Type 'exit' to quit.")
    while True:
        user_input = input("USER: ").strip()
        
        if user_input.lower() == "exit":
            print("Exiting the debate system. Goodbye!")
            break
        
        # Start the debate with the provided topic
        # debate_system.print_streaming(user_input)
        debate_system.stream(user_input)

if __name__ == "__main__":
    main()
