module.exports = {
    after : function(browser) {
        console.log('Closing down...');
        browser.getLog('browser', function(result) {
                                 console.log(result);
                             }).end();
    },
    "Test Fullscreen": function(browser){
        // control the browser
        open_notebook(browser);
        
        browser.restartKernel(2000)
               .executeCell(0)
               .pause(5000).getLog('browser', function(result) {
                                        console.log(result);
                                    })
               .waitForElementVisible(".ipy-widget.widget-container.widget-box", 10);
        
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
        // browser.end();
    }
}


function open_notebook(browser) {
    return browser.url("http://localhost:8889/notebooks/notebooks/TestAuto.ipynb");
}
