use console::Style;
use textwrap::wrap;

use crate::Quote;

/// Format and print a quote. If `original` is provided, it's displayed as the
/// source text below the (translated) main quote.
pub fn format_quote(quote: &Quote, original: Option<&Quote>) {
    let term = console::Term::stdout();
    let width = if term.is_term() {
        (term.size().1 as usize).min(76)
    } else {
        72
    };

    let style = Style::new().italic().dim();

    let pattern = "~*~*-";
    let banner: String = pattern.chars().cycle().take(width).collect();
    println!();
    println!("{}", style.apply_to(&banner));

    let wrapped = wrap(&quote.text, width);
    for line in &wrapped {
        println!("{}", style.apply_to(line));
    }

    if let Some(orig) = original {
        println!();
        let orig_wrapped = wrap(&orig.text, width);
        for line in &orig_wrapped {
            println!("{}", style.apply_to(line));
        }
    }

    println!();

    println!("{}", style.apply_to(format!("-- {} --", quote.figure)));

    println!("{}", style.apply_to(&banner));
    println!();
}

/// Format and print a quote from raw strings, avoiding a Quote allocation.
pub fn format_raw(category: &str, figure: &str, text: &str) {
    let quote = Quote {
        figure: figure.to_string(),
        text: text.to_string(),
        category: category.to_string(),
    };
    format_quote(&quote, None);
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Quote;

    #[test]
    fn test_format_quote_no_panic() {
        let quote = Quote {
            figure: "Test Figure".to_string(),
            text: "This is a test quote.".to_string(),
            category: "Test Category".to_string(),
        };
        // Should not panic
        format_quote(&quote, None);
    }

    #[test]
    fn test_format_raw_no_panic() {
        // Should not panic
        format_raw("Test Category", "Test Figure", "This is a test quote.");
    }

    #[test]
    fn test_format_quote_with_original_no_panic() {
        let quote = Quote {
            figure: "Test Figure".to_string(),
            text: "This is the translated quote.".to_string(),
            category: "Test Category".to_string(),
        };
        let original = Quote {
            figure: "Original Figure".to_string(),
            text: "This is the original quote.".to_string(),
            category: "Original Category".to_string(),
        };
        // Should not panic
        format_quote(&quote, Some(&original));
    }

    #[test]
    fn test_format_quote_long_text_no_panic() {
        let quote = Quote {
            figure: "A Figure With A Very Long Name That Should Still Format Correctly".to_string(),
            text: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. \
                    Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
                    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris \
                    nisi ut aliquip ex ea commodo consequat.".to_string(),
            category: "Test Category".to_string(),
        };
        // Should not panic with long text
        format_quote(&quote, None);
    }
}
