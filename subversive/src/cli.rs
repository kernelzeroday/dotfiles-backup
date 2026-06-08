use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "subversive")]
#[command(about = "Quotes from powerful and subversive figures")]
pub struct Cli {
    #[command(subcommand)]
    pub command: Option<Commands>,
    /// Translate quote (mock: es, fr, de, ru, zh)
    #[arg(short, long)]
    pub translate: Option<String>,
}

#[derive(Subcommand)]
pub enum Commands {
    /// Get a random quote
    Random,
    /// Get a quote from a specific category
    Category {
        category: String,
    },
    /// List all categories
    List,
    /// Search quotes by figure name
    Figure {
        name: String,
    },
    /// Show statistics about the quote database
    Stats,
}
