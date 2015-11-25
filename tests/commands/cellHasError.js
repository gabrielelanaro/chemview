exports.command = function(cellNumber, callback) {
  var self = this;

  this.execute(
     function(cellNumber) {
         var cell = IPython.notebook.get_cell(cellNumber);
         
         if (cell.output_area.outputs.length > 0) {
             var out = cell.output_area.outputs[0];
             if (out.output_type == 'error') {
                 return { output_type: 'error', evalue: out.evalue, ename: out.ename };
             }
         }
    },

    [cellNumber], // arguments array to be passed

    function(result) {
      if (result.value != null) {
        self.assert.ok(result.value.output_type != 'error', "Check that python has no error");
      }
      
      
      if (typeof callback === "function") {    
        callback.call(self, result);
      }
    }
  );

  return this; // allows the command to be chained.
};
