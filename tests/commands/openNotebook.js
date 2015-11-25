exports.command = function(notebookName, callback) {
  return this.url("http://localhost:8889/notebooks/notebooks/" + notebookName); // allows the command to be chained.
};
