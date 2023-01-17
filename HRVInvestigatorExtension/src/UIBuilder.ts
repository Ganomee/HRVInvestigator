import { Widget } from '@lumino/widgets';
import { Message } from '@lumino/messaging';
import { InputDialog } from '@jupyterlab/apputils';

interface APODResponse {
  copyright: string;
  date: string;
  explanation: string;
  media_type: 'video' | 'image';
  title: string;
  url: string;
}

class HRVWidget extends Widget {
  private sidebar: HTMLDivElement;
  private mainContent: HTMLDivElement;
  cellSelector: string[];
  commandSeclector: string[];

  runCommandButton: HTMLButtonElement;
  cellSelectorButton: HTMLButtonElement;
  constructor() {
    super();

    this.addClass('hrv-widget');

    // Add an image element to the panel
    this.sidebar = document.createElement('div');
    this.node.appendChild(this.sidebar);

    // Add a main content element to the panel
    this.mainContent = document.createElement('div');
    this.node.appendChild(this.mainContent);

    //initialise the buttons and selectors
    this.cellSelector = [];
    this.commandSeclector = [];
    this.runCommandButton = document.createElement('button');
    this.cellSelectorButton = document.createElement('button');

    // Request a boolean
    InputDialog.getBoolean({ title: 'Check or not?' }).then(
      (value: { value: boolean | null }) => {
        console.log('boolean ' + value.value);
      }
    );
  }

  /**
   * Handle update requests for the widget.
   */
  async onUpdateRequest(msg: Message): Promise<void> {
    const response = await fetch(
      `https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY&date=${this.randomDate()}`
    );

    if (!response.ok) {
      const data = await response.json();
      if (data.error) {
        this.mainContent.innerText = data.error.message;
      } else {
        this.mainContent.innerText = response.statusText;
      }
      return;
    }

    const data = (await response.json()) as APODResponse;

    if (data.media_type === 'image') {
      // Populate the image
      this.mainContent.title = data.title;
      this.mainContent.innerText = data.title;
      if (data.copyright) {
        this.mainContent.innerText += ` (Copyright ${data.copyright})`;
      }
    } else {
      this.mainContent.innerText = 'Random APOD fetched was not an image.';
    }
  }

  // Get a random date string in YYYY-MM-DD format
  randomDate(): string {
    const start = new Date(2010, 1, 1);
    const end = new Date();
    const randomDate = new Date(
      start.getTime() + Math.random() * (end.getTime() - start.getTime())
    );
    return randomDate.toISOString().slice(0, 10);
  }
}

export { HRVWidget };

// Write a selection widget that allows you to select a notebook

// Write a selection widget that allows you to select a cell
// Write a button that allows you to run the HRV analysis on the selected cell
