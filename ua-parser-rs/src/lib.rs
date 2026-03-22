/// An uap-python Resolver is a callable which returns a PartialResult
/// (~a triplet of optional user_agent, os, and domain). A resolver
/// has lists of matchers for user agents, os, and devices taken in as
/// a Matchers (a 3-uple of lists of matchers).
///
/// A matcher is a callable with a `pattern` and a `flags` properties.
/// But matchers also have additional properties for the replacement
/// information.
///
/// In uap-rs, that's the ua_parser::Extractor doing that, kinda, but
/// it takes a struct from regexes.yaml and parses them in, so
/// probably better leaving that to the Python side and instead
/// exposing individual extractors with convenient interfaces.
///
/// An Extractor is built off of a series of Parsers, which we could
/// get directly from the python side matchers *if those kept the
/// string as `regex` -> swap pattern and regex in the matcher (/
/// rename pattern), and maybe expose regex_flag?
///
/// May not matter as much because pyo3 natively can't piggyback
/// FromPyObject onto Deserialize, this requires the pythonize crate
/// and that seems a bit much for a measly 3 structs... Still, would
/// probably be a good idea for uap-python's matchers to retain the
/// structure of regexes.yaml parsers. Would have been nice to rename
/// them to Parsers as well but that's still very confusing given the
/// global Parser object, unless *that* gets renamed to Extractor on
/// the python side, or something.
use pyo3::prelude::*;
use pyo3::{exceptions::PyValueError, types::PyString};
use std::borrow::Cow::Owned;

type UAParser = (
    String,
    Option<String>,
    Option<String>,
    Option<String>,
    Option<String>,
    Option<String>,
);
#[pyclass(frozen)]
struct UserAgentExtractor(ua_parser::user_agent::Extractor<'static>);
#[pyclass(frozen)]
struct UserAgent {
    #[pyo3(get)]
    family: Py<PyString>,
    #[pyo3(get)]
    major: Option<Py<PyString>>,
    #[pyo3(get)]
    minor: Option<Py<PyString>>,
    #[pyo3(get)]
    patch: Option<Py<PyString>>,
    #[pyo3(get)]
    patch_minor: Option<Py<PyString>>,
}
#[pymethods]
impl UserAgentExtractor {
    #[new]
    fn new(it: &Bound<PyAny>) -> PyResult<Self> {
        use ua_parser::user_agent::{Builder, Parser};
        it.try_iter()?
            .try_fold(Builder::new(), |s, p| {
                let p: UAParser = p?.extract()?;
                s.push(Parser {
                    regex: Owned(p.0),
                    family_replacement: p.1.map(Owned),
                    v1_replacement: p.2.map(Owned),
                    v2_replacement: p.3.map(Owned),
                    v3_replacement: p.4.map(Owned),
                    v4_replacement: p.5.map(Owned),
                })
                .map_err(|e| PyValueError::new_err(e.to_string()))
            })?
            .build()
            .map_err(|e| PyValueError::new_err(e.to_string()))
            .map(Self)
    }
    fn extract(&self, py: Python<'_>, s: &str) -> PyResult<Option<UserAgent>> {
        Ok(self.0.extract(s).map(|v| UserAgent {
            family: PyString::new(py, &v.family).unbind(),
            major: v.major.map(|s| PyString::new(py, s).unbind()),
            minor: v.minor.map(|s| PyString::new(py, s).unbind()),
            patch: v.patch.map(|s| PyString::new(py, s).unbind()),
            patch_minor: v.patch_minor.map(|s| PyString::new(py, s).unbind()),
        }))
    }
}

type OSParser = (
    String,
    Option<String>,
    Option<String>,
    Option<String>,
    Option<String>,
    Option<String>,
);
#[pyclass(frozen)]
struct OSExtractor(ua_parser::os::Extractor<'static>);
#[pyclass(frozen)]
struct OS {
    #[pyo3(get)]
    family: Py<PyString>,
    #[pyo3(get)]
    major: Option<Py<PyString>>,
    #[pyo3(get)]
    minor: Option<Py<PyString>>,
    #[pyo3(get)]
    patch: Option<Py<PyString>>,
    #[pyo3(get)]
    patch_minor: Option<Py<PyString>>,
}
#[pymethods]
impl OSExtractor {
    #[new]
    fn new(it: &Bound<PyAny>) -> PyResult<Self> {
        use ua_parser::os::{Builder, Parser};
        it.try_iter()?
            .try_fold(Builder::new(), |s, p| {
                let p: OSParser = p?.extract()?;
                s.push(Parser {
                    regex: Owned(p.0),
                    os_replacement: p.1.map(Owned),
                    os_v1_replacement: p.2.map(Owned),
                    os_v2_replacement: p.3.map(Owned),
                    os_v3_replacement: p.4.map(Owned),
                    os_v4_replacement: p.5.map(Owned),
                })
                .map_err(|e| PyValueError::new_err(e.to_string()))
            })?
            .build()
            .map_err(|e| PyValueError::new_err(e.to_string()))
            .map(Self)
    }
    fn extract(&self, py: Python<'_>, s: &str) -> PyResult<Option<OS>> {
        Ok(self.0.extract(s).map(|v| OS {
            family: PyString::new(py, &v.os).unbind(),
            major: v.major.map(|s| PyString::new(py, &s).unbind()),
            minor: v.minor.map(|s| PyString::new(py, &s).unbind()),
            patch: v.patch.map(|s| PyString::new(py, &s).unbind()),
            patch_minor: v.patch_minor.map(|s| PyString::new(py, &s).unbind()),
        }))
    }
}

type DeviceParser = (
    String,
    Option<String>,
    Option<String>,
    Option<String>,
    Option<String>,
);
#[pyclass(frozen)]
struct DeviceExtractor(ua_parser::device::Extractor<'static>);
#[pyclass(frozen)]
struct Device {
    #[pyo3(get)]
    family: Py<PyString>,
    #[pyo3(get)]
    brand: Option<Py<PyString>>,
    #[pyo3(get)]
    model: Option<Py<PyString>>,
}
#[pymethods]
impl DeviceExtractor {
    #[new]
    fn new(it: &Bound<PyAny>) -> PyResult<Self> {
        use ua_parser::device::{Builder, Flag, Parser};
        it.try_iter()?
            .try_fold(Builder::new(), |s, p| {
                let p: DeviceParser = p?.extract()?;
                s.push(Parser {
                    regex: Owned(p.0),
                    regex_flag: if p.1.as_deref() == Some("i") {
                        Some(Flag::IgnoreCase)
                    } else {
                        None
                    },
                    device_replacement: p.2.map(Owned),
                    brand_replacement: p.3.map(Owned),
                    model_replacement: p.4.map(Owned),
                })
                .map_err(|e| PyValueError::new_err(e.to_string()))
            })?
            .build()
            .map_err(|e| PyValueError::new_err(e.to_string()))
            .map(Self)
    }
    fn extract(&self, py: Python<'_>, s: &str) -> PyResult<Option<Device>> {
        Ok(self.0.extract(s).map(|v| Device {
            family: PyString::new(py, &v.device).unbind(),
            brand: v.brand.map(|s| PyString::new(py, &s).unbind()),
            model: v.model.map(|s| PyString::new(py, &s).unbind()),
        }))
    }
}

#[pymodule(gil_used = false)]
fn ua_parser_rs(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<UserAgentExtractor>()?;
    m.add_class::<OSExtractor>()?;
    m.add_class::<DeviceExtractor>()?;
    Ok(())
}
