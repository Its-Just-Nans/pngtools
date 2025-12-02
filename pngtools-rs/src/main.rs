use std::process::exit;

use pyo3::{PyResult, Python, types::PyAnyMethods};

fn main() {
    let res_python: PyResult<i32> = Python::attach(|py| {
        let m = py.import("pngtools")?;
        let cli_class = m.getattr("CLI")?;
        // Instantiate: c = CLI()
        let cli_instance = cli_class.call0()?;
        // Call method: exit_code = c.cmdloop()
        let exit_code: i32 = cli_instance.call_method0("cmdloop")?.extract()?;
        Ok(exit_code)
    });
    match res_python {
        Ok(code) => exit(code),
        Err(e) => {
            eprintln!("Error: {}", e);
            exit(1);
        }
    }
}
