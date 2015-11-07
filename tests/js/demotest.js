module.exports = {
    "My test case": function(browser){
        // control the browser
        open_notebook(browser);
        restart_kernel(browser);
        
        execute_cell(browser);
        browser.expect.element(".output_error").not.present;
        browser.expect.element("div.widget-box").present;
        // console.log(browser.getLog())
        // browser.end();
    
    }
}


function open_notebook(browser) {
    return browser.url("http://localhost:8889/notebooks/notebooks/TestAuto.ipynb");
}

function restart_kernel(browser) {
    return browser.click('button[data-jupyter-action="ipython.restart-kernel"]')
                 .pause(1000)
                 .keys([browser.Keys.ENTER]);
}

function execute_cell(browser) {
    return browser
            .assert.visible(".input_area")
            .elementIdClick(".input_area")
            .pause(1000) // Wait for a restart
            .keys([browser.Keys.SHIFT, browser.Keys.ENTER])
            .pause(1500); // Wait for change to take effect
}
