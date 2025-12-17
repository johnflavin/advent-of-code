use anyhow::{Context, Result};
use log::debug;
use std::fs;
use std::path::PathBuf;

pub struct InputManager {
    cache_dir: PathBuf,
    session_token: String,
}

impl InputManager {
    pub fn new() -> Result<Self> {
        // Use resources/inputs directory (shared with Python)
        let cache_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("resources")
            .join("inputs");

        fs::create_dir_all(&cache_dir).context("Failed to create inputs cache directory")?;

        // Read session token from resources/session.txt (shared with Python)
        let session_file = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("resources")
            .join("session.txt");

        let session_token = fs::read_to_string(&session_file)
            .context("Failed to read session.txt. Make sure resources/session.txt exists with your AoC session cookie.")?
            .trim()
            .to_string();

        Ok(Self {
            cache_dir,
            session_token,
        })
    }

    pub fn get_input(&self, year: u16, day: u8) -> Result<String> {
        let cache_file = self.cache_dir.join(format!("{}-12-{:02}.txt", year, day));

        if cache_file.exists() {
            debug!("Reading cached input: {}-12-{:02}", year, day);
            fs::read_to_string(cache_file).context("Failed to read cached input file")
        } else {
            let content = self.download_input(year, day)?;
            fs::write(&cache_file, &content)
                .context("Failed to write downloaded input to cache")?;
            Ok(content)
        }
    }

    fn download_input(&self, year: u16, day: u8) -> Result<String> {
        debug!("Downloading input: {}-12-{}", year, day);
        let url = format!("https://adventofcode.com/{}/day/{}/input", year, day);

        let client = reqwest::blocking::Client::new();
        let response = client
            .get(&url)
            .header("Cookie", format!("session={}", self.session_token))
            .send()
            .context("Failed to send HTTP request to Advent of Code")?
            .error_for_status()
            .context("HTTP request failed (check your session token)")?;

        response
            .text()
            .context("Failed to read response body as text")
    }
}
