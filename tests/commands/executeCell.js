exports.command = function(cellNumber, callback) {
  var self = this;

  this.execute(
     function(cellNumber) {
         console.log("Executing cell number " + cellNumber);
         var cell = IPython.notebook.get_cell(cellNumber);
         cell.execute();
    },

    [cellNumber], // arguments array to be passed

    function(result) {
      if (typeof callback === "function") {
        callback.call(self, result);
      }
    }
  );

  return this; // allows the command to be chained.
};
