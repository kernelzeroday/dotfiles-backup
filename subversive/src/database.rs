use anyhow::Result;
use rand::seq::SliceRandom;
use serde::Deserialize;
use std::collections::HashMap;

const VENDORED_QUOTES: &str = include_str!("../data/quotes.json");

#[derive(Debug, Clone, Deserialize)]
pub struct Quote {
    pub figure: String,
    pub text: String,
    pub category: String,
}

#[derive(Debug, Deserialize)]
pub struct QuoteDatabase {
    quotes: HashMap<String, Vec<Quote>>,
}

#[derive(Debug)]
pub struct Stats {
    pub total_quotes: usize,
    pub total_categories: usize,
    pub total_figures: usize,
    pub top_figures: Vec<(String, usize)>,
    pub category_breakdown: Vec<(String, usize)>,
}

impl QuoteDatabase {
    pub fn load_embedded() -> Result<Self> {
        let db: QuoteDatabase = serde_json::from_str(VENDORED_QUOTES)?;
        Ok(db)
    }

    pub fn total_quotes(&self) -> usize {
        self.quotes.values().map(|v| v.len()).sum()
    }

    pub fn get_random_quote(&self) -> Result<&Quote> {
        use rand::Rng;
        let total = self.total_quotes();
        if total == 0 {
            anyhow::bail!("No quotes available");
        }
        let mut rng = rand::thread_rng();
        let mut target = rng.gen_range(0..total);
        for quotes in self.quotes.values() {
            if target < quotes.len() {
                return Ok(&quotes[target]);
            }
            target -= quotes.len();
        }
        anyhow::bail!("No quotes available");
    }

    pub fn get_quote_from_category(&self, category: &str) -> Result<&Quote> {
        self.quotes
            .get(category)
            .and_then(|quotes| quotes.choose(&mut rand::thread_rng()))
            .ok_or_else(|| anyhow::anyhow!("No quotes found for category: {}", category))
    }

    pub fn list_categories(&self) -> Vec<(&str, usize)> {
        let mut cats: Vec<_> = self
            .quotes
            .iter()
            .map(|(k, v)| (k.as_str(), v.len()))
            .collect();
        cats.sort_by(|a, b| a.0.cmp(b.0));
        cats
    }

    /// Search quotes by figure name (case-insensitive substring match).
    /// Returns vec of (category, figure, text) for all matching quotes.
    pub fn search_figures(&self, query: &str) -> Vec<(&str, &str, &str)> {
        let query_lower = query.to_lowercase();
        let mut results = Vec::new();
        for (category, quotes) in &self.quotes {
            for quote in quotes {
                if quote.figure.to_lowercase().contains(&query_lower) {
                    results.push((
                        category.as_str(),
                        quote.figure.as_str(),
                        quote.text.as_str(),
                    ));
                }
            }
        }
        results
    }

    /// Compute aggregate statistics about the quote database.
    pub fn get_stats(&self) -> Stats {
        let total_quotes = self.total_quotes();
        let total_categories = self.quotes.len();

        let mut figure_counts: HashMap<&str, usize> = HashMap::new();
        for quotes in self.quotes.values() {
            for quote in quotes {
                *figure_counts.entry(quote.figure.as_str()).or_insert(0) += 1;
            }
        }

        let total_figures = figure_counts.len();

        let mut top_figures: Vec<_> = figure_counts.into_iter().collect();
        top_figures.sort_by_key(|k| std::cmp::Reverse(k.1));
        top_figures.truncate(10);
        let top_figures: Vec<(String, usize)> = top_figures
            .into_iter()
            .map(|(name, count)| (name.to_string(), count))
            .collect();

        let mut category_breakdown: Vec<_> = self
            .quotes
            .iter()
            .map(|(name, quotes)| (name.clone(), quotes.len()))
            .collect();
        category_breakdown.sort_by(|a, b| a.0.cmp(&b.0));

        Stats {
            total_quotes,
            total_categories,
            total_figures,
            top_figures,
            category_breakdown,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_db() -> QuoteDatabase {
        QuoteDatabase::load_embedded().expect("Failed to load embedded quotes")
    }

    #[test]
    fn test_load_embedded() {
        let db = test_db();
        assert!(db.total_quotes() > 0, "Database should be non-empty");
    }

    #[test]
    fn test_total_quotes() {
        let db = test_db();
        let count = db.total_quotes();
        assert!(count > 0, "Database should have quotes");
    }

    #[test]
    fn test_get_random_quote() {
        let db = test_db();
        let quote = db.get_random_quote().expect("Should get a random quote");
        assert!(!quote.figure.is_empty(), "Figure should be non-empty");
        assert!(!quote.text.is_empty(), "Text should be non-empty");
        assert!(!quote.category.is_empty(), "Category should be non-empty");
    }

    #[test]
    fn test_get_quote_from_category() {
        let db = test_db();
        let quote = db
            .get_quote_from_category("US Politicians")
            .expect("Should find quotes in US Politicians");
        assert_eq!(quote.category, "US Politicians");
    }

    #[test]
    fn test_get_quote_from_category_invalid() {
        let db = test_db();
        let result = db.get_quote_from_category("NonexistentCategoryXYZ");
        assert!(result.is_err(), "Should return error for invalid category");
    }

    #[test]
    fn test_list_categories() {
        let db = test_db();
        let categories = db.list_categories();
        assert!(!categories.is_empty(), "Should have categories");
        // Verify sorted alphabetically
        for i in 1..categories.len() {
            assert!(
                categories[i - 1].0 <= categories[i].0,
                "Categories should be sorted alphabetically"
            );
        }
        // Check known category exists
        assert!(categories.iter().any(|(name, _)| *name == "US Politicians"));
        // Should have more than 0 categories
        assert!(categories.len() > 0);
    }

    #[test]
    fn test_search_figures() {
        let db = test_db();
        let results = db.search_figures("Henry Kissinger");
        assert!(!results.is_empty(), "Should find Henry Kissinger");
        for (category, figure, text) in &results {
            assert!(
                figure.to_lowercase().contains("henry kissinger"),
                "Figure should match query"
            );
            assert!(!category.is_empty(), "Category should be non-empty");
            assert!(!text.is_empty(), "Text should be non-empty");
        }
        // Verify case-insensitive search returns same results
        let results_lower = db.search_figures("henry kissinger");
        assert_eq!(
            results.len(),
            results_lower.len(),
            "Case-insensitive search should return same results"
        );
    }

    #[test]
    fn test_search_figures_no_match() {
        let db = test_db();
        let results = db.search_figures("NonexistentFigure123");
        assert!(results.is_empty(), "Should return empty for nonexistent figure");
    }

    #[test]
    fn test_get_stats() {
        let db = test_db();
        let stats = db.get_stats();
        assert_eq!(stats.total_quotes, db.total_quotes());
        assert_eq!(stats.total_categories, db.quotes.len());
        assert!(stats.total_figures > 0, "Should have figures");
        assert!(!stats.top_figures.is_empty(), "Should have top figures");
        assert!(
            stats.top_figures.len() <= 10,
            "Top figures should be at most 10"
        );
        // Verify top figures sorted by count descending
        for i in 1..stats.top_figures.len() {
            assert!(
                stats.top_figures[i - 1].1 >= stats.top_figures[i].1,
                "Top figures should be sorted by count descending"
            );
        }
        // Category breakdown should be sorted by name
        for i in 1..stats.category_breakdown.len() {
            assert!(
                stats.category_breakdown[i - 1].0 <= stats.category_breakdown[i].0,
                "Category breakdown should be sorted alphabetically"
            );
        }
    }
}
