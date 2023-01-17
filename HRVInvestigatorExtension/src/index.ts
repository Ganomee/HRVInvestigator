import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';
import { INotebookTracker } from '@jupyterlab/notebook';
import { HRVInvestigatorData } from './DataHandler';
import { HRVWidget } from './UIBuilder';

/**
 * Initialization data for the HRVInvestigator extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'HRVInvestigator:plugin',
  autoStart: true,
  requires: [ICommandPalette, INotebookTracker],
  optional: [ISettingRegistry],
  activate: activate
};

/**
 * Activation function for the HRVInvestigator extension.
 * @param app
 * @param palette
 * @param notebookTracker
 * @param settingRegistry
 */
function activate(
  app: JupyterFrontEnd,
  palette: ICommandPalette,
  notebookTracker: INotebookTracker,
  settingRegistry: ISettingRegistry | null
): void {
  console.log('JupyterLab extension HRVInvestigator is activated!');
  // @ts-ignore
  let _dataHandler: HRVInvestigatorData;

  // Create a blank content widget inside a MainAreaWidget
  const content = new HRVWidget();
  const widget = new MainAreaWidget({ content });
  widget.id = 'hrvi-jupyterlab';
  widget.title.label = 'HRVInvestigator';
  widget.title.closable = true;

  // Add an image element to the content
  const img = document.createElement('img');
  content.node.appendChild(img);

  // Add an application command
  const command = 'hrvi:open';
  app.commands.addCommand(command, {
    label: 'Open HRVInvestigator',
    execute: () => {
      if (!widget.isAttached) {
        // Attach the widget to the main work area if it's not there
        app.shell.add(widget, 'main');
      }
      // Refresh the picture in the widget
      content.update();
      // Activate the widget
      app.shell.activateById(widget.id);
      const currentNotebook = notebookTracker.currentWidget;
      if (currentNotebook) {
        _dataHandler = new HRVInvestigatorData(currentNotebook);
      }
    }
  });
  // Add the command to the palette.
  palette.addItem({ command, category: 'Tutorial' });

  // Just Settings - We can ignore this
  if (settingRegistry) {
    settingRegistry
      .load(plugin.id)
      .then(settings => {
        console.log('HRVInvestigator settings loaded:', settings.composite);
      })
      .catch(reason => {
        console.error('Failed to load settings for HRVInvestigator.', reason);
      });
  }
}

export default plugin;
