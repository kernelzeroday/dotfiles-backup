use anyhow::Result;
use clap::Parser;
use console::Style;
use subversive::*;

fn print_category_line(cat: &str, count: usize, dim: &Style) {
    println!(
        "  {} {} {}",
        cat,
        dim.apply_to("·"),
        dim.apply_to(format!("{} quotes", count))
    );
}

/// Display a single quote, optionally alongside a translation.
fn display_with_translation(quote: &Quote, translate_lang: Option<&str>) {
    let translated = translate_lang.map(|lang| {
        let translated_text = translate_text(&quote.text, lang);
        Quote {
            figure: quote.figure.clone(),
            text: translated_text,
            category: quote.category.clone(),
        }
    });

    if let Some(ref t) = translated {
        format_quote(t, Some(quote));
    } else {
        format_quote(quote, None);
    }
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    let db = QuoteDatabase::load_embedded()?;

    match cli.command {
        Some(Commands::Random) | None => {
            let quote = db.get_random_quote()?;
            display_with_translation(quote, cli.translate.as_deref());
        }
        Some(Commands::Category { ref category }) => {
            let quote = db.get_quote_from_category(category)?;
            display_with_translation(quote, cli.translate.as_deref());
        }
        Some(Commands::List) => {
            let bold = Style::new().bold();
            let dim = Style::new().dim();
            println!(
                "\n  {} categories, {} total quotes\n",
                bold.apply_to(db.list_categories().len()),
                bold.apply_to(db.total_quotes())
            );
            for (cat, count) in db.list_categories() {
                print_category_line(cat, count, &dim);
            }
            println!();
        }
        Some(Commands::Figure { ref name }) => {
            let results = db.search_figures(name);
            if results.is_empty() {
                println!("No figures found matching: {}", name);
            } else {
                for (category, figure, text) in results {
                    format_raw(category, figure, text);
                }
            }
        }
        Some(Commands::Stats) => {
            let stats = db.get_stats();
            let bold = Style::new().bold();
            let dim = Style::new().dim();
            println!(
                "\n  {} {} {}",
                bold.apply_to("Statistics"),
                dim.apply_to("·"),
                dim.apply_to("subversive quotes")
            );
            println!();
            println!(
                "  {} quotes across {} categories from {} figures",
                bold.apply_to(stats.total_quotes.to_string()),
                bold.apply_to(stats.total_categories.to_string()),
                bold.apply_to(stats.total_figures.to_string())
            );
            println!();
            println!("  {}", bold.apply_to("Top 10 Figures"));
            for (i, (figure, count)) in stats.top_figures.iter().enumerate() {
                println!("  {}. {} ({})", i + 1, figure, count);
            }
            println!();
            println!("  {}", bold.apply_to("Category Breakdown"));
            for (cat, count) in &stats.category_breakdown {
                print_category_line(cat, *count, &dim);
            }
            println!();
        }
    }

    Ok(())
}
