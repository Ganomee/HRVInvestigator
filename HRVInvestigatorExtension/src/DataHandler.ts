import { CodeCellModel } from '@jupyterlab/cells';
import { NotebookPanel } from '@jupyterlab/notebook';

class HRVInvestigatorData {
  // Variables used in setup
  activeNotebookPanel: NotebookPanel;
  codeCells: CodeCellModel[];
  lastActiveValue: Record<string, unknown>;

  constructor(notebookPanel: NotebookPanel) {
    this.lastActiveValue = {};
    this.activeNotebookPanel = notebookPanel;
    this.codeCells = [];
    if (!this.activeNotebookPanel.model?.cells) {
      return;
    }

    for (let i = 0; i < this.activeNotebookPanel.model.cells.length; i++) {
      const cell = this.activeNotebookPanel.model.cells.get(i);
      if (cell instanceof CodeCellModel) {
        this.codeCells.push(cell);
        // TODO remove
        const outputs = cell.outputs;
        if (!outputs) {
          return;
        }
        for (let j = 0; j < outputs.length; j++) {
          const output = outputs.get(j);
          console.log('\t\t', output.data);
        }
      }
    }
  }

  /** Creates a List of all available CodeCells for selection TODO
   * @returns {string[]} List of all available CodeCells for selection
   */
  getCodeCellsSelector() {
    return this.codeCells.map((cell, index) => {
      cell.outputs;
    });
  }

  /**
   * @returns {} The data of the specified code cell
   * @param cellindex The index of the code cell
   */
  getDataFromCell(cellindex: number) {
    return this.codeCells[cellindex].outputs;
  }
}

export { HRVInvestigatorData };
