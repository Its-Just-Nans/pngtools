//! pngtools main

use pyo3::PyResult;
use std::process::exit;

fn main() {
    let res_python: PyResult<i32> = pngtools::run_cli();
    match res_python {
        Ok(code) => exit(code),
        Err(e) => {
            eprintln!("Error: {}", e);
            exit(1);
        }
    }
}
