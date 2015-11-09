module.exports = {
    "Test Fullscreen": function(browser){
        // control the browser
        open_notebook(browser);
        restart_kernel(browser);
        
        execute_cell(browser);
        browser.expect.element(".output_error").not.present;
        
        var CANVAS_SEL = ".ipy-widget.widget-container.widget-box canvas";
        browser.expect.element(CANVAS_SEL)
               .to.have.css("width").which.equals("300px");
               
        // Now we doubleclick on it
        browser.moveToElement(CANVAS_SEL, 2, 2).doubleClick();
        browser.expect.element(CANVAS_SEL)
               .to.have.css("width").which.not.equals("300px");
        
        // browser.pause(1000).keys([browser.Keys.ESC]).pause(1000);
        // browser.expect.element(CANVAS_SEL)
        //        .to.have.css("width").which.equals("300px");
        
        browser.end();
    }
}


function open_notebook(browser) {
    return browser.url("http://localhost:8889/notebooks/notebooks/TestAuto.ipynb");
}

function restart_kernel(browser) {
    return browser.click('button[data-jupyter-action="ipython.restart-kernel"]')
                 .pause(2000)
                 .keys([browser.Keys.ENTER]);
}

function execute_cell(browser) {
    return browser
            .assert.visible(".input_area")
            .elementIdClick(".input_area")
            .pause(1000) 
            .keys([browser.Keys.SHIFT, browser.Keys.ENTER])
            .waitForElementVisible(".ipy-widget.widget-container.widget-box", 3000); // Wait for change to take effect
}
