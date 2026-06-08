#!/usr/bin/env python3
"""
Quote Generator - Outputs quotes from politically powerful and subversive figures.
Includes politicians, tech leaders, conspiracy figures, and other influential personalities.
"""

import random
import sys
from typing import Dict, List, Tuple

class QuoteGenerator:
    def __init__(self):
        self.quotes = self._build_quote_database()
    
    def _build_quote_database(self) -> Dict[str, List[Tuple[str, str]]]:
        """Build a database of quotes organized by category/figure."""
        return {
            "Politicians": [
                ("Barack Obama", "The best way to not feel hopeless is to get up and do something."),
                ("Barack Obama", "Change will not come if we wait for some other person or some other time."),
                ("George W. Bush", "There's an old saying in Tennessee — I know it's in Texas, probably in Tennessee — that says, fool me once, shame on — shame on you. Fool me — you can't get fooled again."),
                ("George W. Bush", "I'm the decider, and I decide what is best."),
                ("Benjamin Netanyahu", "The truth is that if Israel were to put down its arms there would be no more Israel. If the Arabs were to put down their arms there would be no more war."),
                ("Benjamin Netanyahu", "The Palestinians want a state, but they have to give peace in return."),
            ],
            "Tech Leaders": [
                ("Sam Altman", "I think AGI is going to be the most important technology ever created by humanity."),
                ("Sam Altman", "The future is going to be weird."),
                ("Dario Amodei", "I think AI safety is really important."),
                ("Dario Amodei", "We need to think carefully about how we develop these systems."),
            ],
            "Historical Figures": [
                ("Osama bin Laden", "We love death. The U.S. loves life. That is the difference between us two."),
                ("Osama bin Laden", "I tell you, freedom and human rights in America are doomed."),
                ("John D. Rockefeller", "I would rather earn 1% off a 100 people's efforts than 100% of my own efforts."),
                ("Andrew Carnegie", "The man who dies thus rich dies disgraced."),
                ("J.P. Morgan", "A man always has two reasons for doing anything: a good reason and the real reason."),
            ],
            "Conspiracy & Alternative Figures": [
                ("David Icke", "The truth is out there, but it's not what most people think."),
                ("Alex Jones", "There's a war on for your mind!"),
                ("Julian Assange", "If wars can be started by lies, peace can be started by truth."),
                ("Edward Snowden", "Privacy matters. Privacy is what allows us to determine who we are and who we want to be."),
            ],
            "UFO & Paranormal": [
                ("Bob Lazar", "The technology I was exposed to was far beyond anything we have publicly."),
                ("Steven Greer", "We are not alone in the universe."),
                ("John Podesta", "My biggest failure of 2014 was not securing the disclosure of the UFO files."),
            ],
            "Secret Societies": [
                ("Henry Kissinger", "The illegal we do immediately. The unconstitutional takes a little longer."),
                ("Zbigniew Brzezinski", "It is easier to kill a million people than it is to control them."),
                ("David Rockefeller", "We are grateful to the Washington Post, The New York Times, Time Magazine and other publications whose directors have attended our meetings and respected their promises of discretion for almost forty years."),
            ]
        }
    
    def get_random_quote(self) -> Tuple[str, str, str]:
        """Return a random quote with figure and category."""
        category = random.choice(list(self.quotes.keys()))
        quotes_in_category = self.quotes[category]
        figure, quote = random.choice(quotes_in_category)
        return figure, category, quote
    
    def get_quote_by_category(self, category: str) -> Tuple[str, str, str]:
        """Return a random quote from a specific category."""
        if category not in self.quotes:
            raise ValueError(f"Category '{category}' not found. Available categories: {list(self.quotes.keys())}")
        
        quotes_in_category = self.quotes[category]
        figure, quote = random.choice(quotes_in_category)
        return figure, category, quote
    
    def list_categories(self) -> List[str]:
        """Return list of available categories."""
        return list(self.quotes.keys())
    
    def format_quote(self, figure: str, category: str, quote: str) -> str:
        """Format the quote for display."""
        separator = "─" * 60
        return f"\n{separator}\n📢 {figure} ({category})\n\n\"{quote}\"\n{separator}\n"

def main():
    """Main function to run the quote generator."""
    generator = QuoteGenerator()
    
    if len(sys.argv) > 1:
        try:
            category = sys.argv[1]
            figure, cat, quote = generator.get_quote_by_category(category)
        except ValueError as e:
            print(f"Error: {e}")
            print(f"Available categories: {', '.join(generator.list_categories())}")
            return
    else:
        figure, category, quote = generator.get_random_quote()
    
    output = generator.format_quote(figure, category, quote)
    print(output)

if __name__ == "__main__":
    main()
