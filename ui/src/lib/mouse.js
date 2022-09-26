export const mouse = {
    button : false,
    x : 0,
    y : 0,
    down : false,
    up : false,
    element : null,
    event(e) {
        const m = mouse;
        m.bounds = m.element.getBoundingClientRect();
        let x = e.pageX - m.bounds.left - scrollX;
        let y = e.pageY - m.bounds.top - scrollY;
        m.x = x;
        m.y = y;
        if(x < 0 || y < 0 || x >= m.element.width || y >= m.element.height){
          return;
        }
        const prevButton = m.button;
        m.button = e.type === "mousedown" ? true : e.type === "mouseup" ? false : mouse.button;
        if (!prevButton && m.button) { m.down = true }
        if (prevButton && !m.button) { m.up = true }
    },
    start(element) {
        mouse.element = element;
        "down,up,move".split(",").forEach(name => document.addEventListener("mouse" + name, mouse.event));
    }
}
