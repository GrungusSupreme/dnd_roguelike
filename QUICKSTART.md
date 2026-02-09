#!/usr/bin/env python3
"""
Quick start guide for the D&D Roguelike GUI.

This file demonstrates the different ways to run the game.
"""

print("""
╔════════════════════════════════════════════════════════════════╗
║         D&D Roguelike - Tactical Wave Survival Game           ║
╚════════════════════════════════════════════════════════════════╝

TWO WAYS TO PLAY:

1. PYGAME GUI (RECOMMENDED)
   ────────────────────────
   Run:  python main_gui.py
   
   Features:
   • Visual 64x64 battle grid
   • 8x8 defended keep area (green highlight)
   • Click to move within keep
   • Auto-combat when enemies are adjacent
   • Real-time enemy movement toward keep
   • Visual health bars and enemy positions

2. TERMINAL (INTERACTIVE TEXT)
   ──────────────────────────────
   Run:  python main.py --interactive
   
   Features:
   • Full turn-based control
   • Character customization with point-buy
   • Color-coded feedback
   • Fast/slow modes with --no-delay
   
   Options:
   • --interactive, -i     Can choose actions each turn
   • --create-character    Run character creator first
   • --seed <n>           Reproducible runs
   • --waves <n>          Number of waves (default: 3)
   • --no-delay           Skip round delays

QUICK START:
────────────
1. Try the GUI first:
   python main_gui.py --seed 42
   
2. Create a custom character and play terminal version:
   python main.py --create-character --interactive --no-delay

3. Run tests to verify everything works:
   python -m unittest discover -s tests -p "test_*.py" -v

═══════════════════════════════════════════════════════════════════
""")
