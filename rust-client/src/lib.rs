use wasm_bindgen::prelude::*;

#[wasm_bindgen(start)]
pub fn start() -> Result<(), JsValue> {
    let window = web_sys::window().ok_or_else(|| JsValue::from_str("No window"))?;
    let document = window.document().ok_or_else(|| JsValue::from_str("No document"))?;
    let status = document.get_element_by_id("status").ok_or_else(|| JsValue::from_str("Missing status element"))?;
    status.set_text_content(Some("Rust/WASM initialized. Gameplay and multiplayer are not implemented yet."));
    Ok(())
}
