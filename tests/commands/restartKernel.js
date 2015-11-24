exports.command = function(timeout, callback) {
  var self = this;

  this.execute(
     function() {
        IPython.notebook.kernel.restart();
    },

    null, // arguments array to be passed

    function(result) {
      self.pause(timeout);
      if (typeof callback === "function") {
        callback.call(self, result);
      }
    }
  );

  return this; // allows the command to be chained.
};
