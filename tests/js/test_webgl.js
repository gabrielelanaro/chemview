module.exports = {
    "Test Fullscreen": function(browser){
        // control the browser
        browser.openNotebook("TestAuto.ipynb");
        
        browser.restartKernel(2000)
               .executeCell(0)
               .pause(3000)
               .cellHasError(0);
        
        if (! (process.env.CI == "true") ) {
            browser.waitForElementVisible(".ipy-widget.widget-container.widget-box", 10);
            
            var CANVAS_SEL = ".ipy-widget.widget-container.widget-box canvas";
            browser.expect.element(CANVAS_SEL)
                   .to.have.css("width").which.equals("300px");
                   
            // Now we doubleclick on it
            browser.moveToElement(CANVAS_SEL, 2, 2).doubleClick();
            browser.expect.element(CANVAS_SEL)
                   .to.have.css("width").which.not.equals("300px");
        }
        
        browser.end();

    },
    
    "Test different shapes": function (browser) {
        browser.openNotebook("TestNotebook.ipynb");
        
        browser.restartKernel(2000);
        for ( var i = 0; i < 23 ; i++) {
           browser.executeCell(i)
                  .pause(1000)
                  .cellHasError(i);
        }
        
        browser.end();
    }
    
}
