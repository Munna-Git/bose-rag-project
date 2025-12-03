"""
✏️ SIMPLE EXAMPLE: Where You Type Your Questions
This is the SIMPLEST way to use MCP - just edit this file!
"""

from mcp_client import MCPClient
import json
import csv
import re
from datetime import datetime

# ============================================================
# STEP 1: Connect to MCP Server
# ============================================================
print("Connecting to MCP server...")
client = MCPClient("http://localhost:8001")

# ============================================================
# STEP 2: TYPE YOUR QUESTIONS HERE! ✏️
# ============================================================

# List all your questions in this array:
MY_QUESTIONS = [
    "WWhat is the maximum number of analog line-level outputs on the EX-1280, and is this different from the EX-1280C?",
    "Comparing the DM8`xxxxxx``e lowest Net Weight in kg? If this lighter speaker is installed outside, what is its stated IP rating? ",
    "We need the lowest latency possible, and redundancy is critical. Between the EX-1280 and EX-1280C, which processor can offer dual-port Dante redundancy and the best guaranteed audio latency (Analog In to Out)? ",
    "If I must wire a speaker in its 100V maximum tap setting, which DM speaker model can handle the least amount of long-term continuous power, and what is that value in Watts? ",
    "If a project strictly requires the use of an RS-232 serial control port for system integration, does the model EX-1280 offer this feature, or is it exclusive to the conferencing EX-1280C? ",
    "Which of the two DesignMax speakers has the lowest Net Weight in kg? If this lighter speaker is installed outside, what is its stated IP rating? ",
    "What is the list price for the ControlSpace EX-1280 when purchased directly from a Bose distributor? ",
    "What is the official warranty length for the DM6PE, and does that warranty cover installation damage? ",
    "What is the minimum required NovaOS firmware version needed for the EX-1280C to handle its 2-line VoIP feature? ",
    "How does the sound dispersion pattern of the DM8SE compare to the DM6PE in a small room, and which one has a more powerful bass response? ",
    "What are the planned successor models for the ControlSpace EX-1280 line scheduled for release in Q1 2026? ",
    "What is the maximum input level (in dBu) on the EX-1280C, and what is the smallest transformer tap available on the DM6PE for a 70 V system? ",
    "If I use the EX-1280 to process audio for four DM8SE speakers wired to four different analog outputs, how many total unused analog inputs will remain on the processor? ",
    "What is the Maximum Input Voltage required for the EX-1280C? Can the DM8SE loudspeaker withstand the same voltage in its 100 V tap setting? ",
    "Using the EX-1280C, if I configure all analog inputs for +48V phantom power, how many GPO outputs are available to interface with a third-party control system? ",
    "We need to use the speaker with the lowest overall physical depth (D) and connect it to the processor that is designed specifically for an office conference room. Name the specific model and state its depth. "


]

# ============================================================
# STEP 3: Run This Script!
# ============================================================

# Store results for CSV export
results = []

print("\n" + "="*70)
print("  ASKING YOUR QUESTIONS")
print("="*70 + "\n")

for i, question in enumerate(MY_QUESTIONS, 1):
    print(f"\n{'─'*70}")
    print(f"Question {i}: {question}")
    print('─'*70)
    
    try:
        # This calls your RAG system via MCP!
        response = client.query_documentation(question)
        
        # Parse response to extract details
        if 'content' in response and len(response['content']) > 0:
            # Combine all content parts
            full_response = ""
            for content_item in response['content']:
                full_response += content_item.get('text', '')
            
            # Extract components using regex
            answer_match = re.search(r'\*\*Answer:\*\*\s*(.*?)(?=\n\n|\*\*)', full_response, re.DOTALL)
            confidence_match = re.search(r'\*\*Confidence:\*\*\s*(\d+)%\s*\((\w+)\)', full_response)
            time_match = re.search(r'\*\*Query Time:\*\*\s*([\d.]+s)', full_response)
            sources_match = re.search(r'\*\*Sources:\*\*\s*(.*?)(?=\n\n|\*\*Query Time)', full_response, re.DOTALL)
            
            answer = answer_match.group(1).strip() if answer_match else "No answer extracted"
            confidence_pct = confidence_match.group(1) if confidence_match else "N/A"
            confidence_label = confidence_match.group(2) if confidence_match else "N/A"
            query_time = time_match.group(1) if time_match else "N/A"
            sources = sources_match.group(1).strip() if sources_match else "N/A"
            
            # Display formatted output
            print(f"\n✅ Answer: {answer}")
            print(f"📊 Confidence: {confidence_pct}% ({confidence_label})")
            print(f"⏱️  Time: {query_time}")
            print(f"📚 Sources: {sources[:100]}..." if len(sources) > 100 else f"📚 Sources: {sources}")
            
            # Store for CSV
            results.append({
                'Question #': i,
                'Question': question,
                'Answer': answer,
                'Confidence (%)': confidence_pct,
                'Confidence Level': confidence_label,
                'Time Taken': query_time,
                'Sources': sources.replace('\n', ' | ')
            })
        else:
            print("❌ No answer received")
            results.append({
                'Question #': i,
                'Question': question,
                'Answer': 'ERROR: No response',
                'Confidence (%)': 'N/A',
                'Confidence Level': 'N/A',
                'Time Taken': 'N/A',
                'Sources': 'N/A'
            })
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure MCP server is running:")
        print("   python mcp_server.py")
        results.append({
            'Question #': i,
            'Question': question,
            'Answer': f'ERROR: {str(e)}',
            'Confidence (%)': 'N/A',
            'Confidence Level': 'N/A',
            'Time Taken': 'N/A',
            'Sources': 'N/A'
        })
        break

print("\n" + "="*70)
print("  ALL QUESTIONS ANSWERED!")
print("="*70)

# ============================================================
# STEP 4: Export to CSV for Excel
# ============================================================
if results:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"bose_rag_results_{timestamp}.csv"
    
    print(f"\n📊 Exporting results to CSV: {csv_filename}")
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Question #', 'Question', 'Answer', 'Confidence (%)', 'Confidence Level', 'Time Taken', 'Sources']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(results)
    
    print(f"✅ Results saved to: {csv_filename}")
    print(f"📈 Total Questions: {len(results)}")
    
    # Calculate summary statistics
    valid_confidences = [int(r['Confidence (%)']) for r in results if r['Confidence (%)'].isdigit()]
    if valid_confidences:
        avg_confidence = sum(valid_confidences) / len(valid_confidences)
        print(f"📊 Average Confidence: {avg_confidence:.1f}%")
    
    high_conf = sum(1 for r in results if r['Confidence Level'] == 'high')
    medium_conf = sum(1 for r in results if r['Confidence Level'] == 'medium')
    low_conf = sum(1 for r in results if r['Confidence Level'] in ['low', 'very_low'])
    
    print(f"✅ High Confidence: {high_conf}")
    print(f"⚠️  Medium Confidence: {medium_conf}")
    print(f"❌ Low Confidence: {low_conf}")
    
    print(f"\n💡 Open {csv_filename} in Excel to view all results!")
    print("   You can add charts, formatting, and analysis to showcase the system!")

print("\n" + "="*70)
print("  SESSION COMPLETE!")
print("="*70)

# ============================================================
# HOW TO USE THIS FILE:
# ============================================================
print("""
╔══════════════════════════════════════════════════════════════════════╗
║                         HOW TO USE THIS                              ║
╚══════════════════════════════════════════════════════════════════════╝

1. Start MCP Server (in one terminal):
   python mcp_server.py

2. Edit this file (my_questions.py):
   - Find MY_QUESTIONS array (line 16)
   - Add your questions to the list
   - Save the file

3. Run this file (in another terminal):
   python my_questions.py

4. See your answers!

EXAMPLE:
────────
MY_QUESTIONS = [
    "What is the power of DM8SE?",      ← Already here
    "How many channels in EX-1280?",    ← Add yours!
    "What is the coverage pattern?",    ← Add yours!
]

That's it! No need to understand MCP internals.
Just add questions and run!
""")
