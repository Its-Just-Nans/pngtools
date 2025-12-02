//! pngtools
//!
//! Python bindings to `pngtools` CLI
//!
//! ```
//! cargo install pngtools --locked
//!
//! pngtools
//! ```

#![warn(clippy::all, rust_2018_idioms)]
#![deny(
    missing_docs,
    clippy::all,
    clippy::missing_docs_in_private_items,
    clippy::missing_errors_doc,
    clippy::missing_panics_doc,
    clippy::cargo
)]
#![warn(clippy::multiple_crate_versions)]

use pyo3::{PyResult, Python, types::PyAnyMethods};

/// pngtools cli
/// # Errors
/// Return a [`pyo3::PyResult`] if an error happen
pub fn run_cli() -> PyResult<i32> {
    Python::attach(|py| {
        let m = py.import("pngtools")?;
        let cli_class = m.getattr("CLI")?;
        // Instantiate: c = CLI()
        let cli_instance = cli_class.call0()?;
        // Call method: exit_code = c.cmdloop()
        let exit_code: i32 = cli_instance.call_method0("cmdloop")?.extract()?;
        Ok(exit_code)
    })
}
