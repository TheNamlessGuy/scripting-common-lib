/**
 * A class for (optionally) saving all your plugin data in bookmark format.
 * When syncing plugin data, you're limited to about 100KiB. But, you're not limited to how many bookmarks you can sync, nor how big they can be.
 *
 * TODO: All the "public" functions should check for if bookmarks permission is available
 */
class BaseOptions {
  constructor() { throw Error(`${this.constructor.name} is abstract`); }

  /**
   * ::get will return this if it's not null. To be overridden in child classes.
   * @type {Record<string, any>}
   */
  static DEFAULT = null;
  /**
   * Used to chunk the save data JSON
   * @type {number}
   */
  static MAX_BYTE_LENGTH = 40000;

  /**
   * @returns {Record<string, any>}
   */
  static async get() {
    const hasBookmarkSaves = await this.hasBookmarkSaves();

    let retval = null;
    if (hasBookmarkSaves) {
      retval = await this._getBookmarkData();
    } else {
      retval = await browser.storage.local.get();
      if (retval != null && Object.keys(retval).length === 0) { // browser.storage.local.get() seemingly always returns an object, even if the plugin never saved any data. Incredibly strange
        retval = null;
      }
    }

    if (retval == null && this.DEFAULT != null) {
      return JSON.parse(JSON.stringify(this.DEFAULT));
    } else {
      return retval;
    }
  }

  /**
   * @param {Record<string, any>} opts
   * @param {Partial<{saveUsingBookmark: boolean}>} extras
   * @returns {Promise<void>}
   */
  static async set(opts, extras = {}) {
    const saveUsingBookmark = extras?.saveUsingBookmark ?? false;

    if (saveUsingBookmark) {
      await this._setBookmarkData(opts);
      await browser.storage.local.clear();
    } else {
      await browser.storage.local.set(opts);
      await this._clearBookmarkData();
    }
  }

  /**
   * @returns {string[]}
   */
  static getBookmarkLocation() {
    return ['menu________', 'Plugin data', this._pluginID()];
  }

  /**
   * @returns {Promise<boolean>}
   */
  static async hasBookmarkSaves() {
    return (await this._getBookmarks()).length > 0;
  }

  /**
   * @returns {string}
   */
  static _pluginID() {
    return browser.runtime.getManifest().browser_specific_settings.gecko.id;
  }

  /**
   * @returns {string}
   */
  static _baseBookmarkURL() {
    const id = this._pluginID().split('@');
    return `${id[0]}://${id[1]}`;
  }

  /**
   * @returns {string[]}
   */
  static _chunk(string, maxByteLength) {
    const encoder = new TextEncoder();
    const retval = [];

    let current = '';
    for (const c of string) {
      const bytes = encoder.encode(current + c).length;
      if (bytes > maxByteLength) {
        retval.push(current);
        current = c;
      } else {
        current += c;
      }
    }

    if (current.length > 0) {
      retval.push(current);
    }

    return retval;
  }

  /**
   * @param {Record<string, any>} opts
   * @returns {string[]}
   */
  static _bookmarkURLs(opts) {
    const url = this._baseBookmarkURL();

    const chunks = this._chunk(encodeURIComponent(JSON.stringify(opts)), this.MAX_BYTE_LENGTH);

    const retval = [];
    for (let c = 0; c < chunks.length; ++c) {
      const chunkURL = new URL(url);
      chunkURL.searchParams.set('i', c);
      chunkURL.searchParams.set('d', chunks[c]);
      retval.push(chunkURL.toString());
    }

    return retval;
  }

  /**
   * @returns {Promise<BrowserBookmark[]>}
   */
  static async _getBookmarks() {
    const prefix = this._baseBookmarkURL();
    const bookmarks = (await browser.bookmarks.search({query: prefix})).filter(x => x.url.startsWith(prefix));
    bookmarks.sort((a, b) => {
      const ai = parseInt(new URL(a.url).searchParams.get('i'), 10);
      const bi = parseInt(new URL(b.url).searchParams.get('i'), 10);
      return ai - bi;
    });
    return bookmarks;
  }

  /**
   * @returns {Promise<Record<string, any>|null>}
   */
  static async _getBookmarkData() {
    const bookmarks = await this._getBookmarks();
    if (bookmarks.length === 0) {
      return null;
    }

    let json = '';
    for (const bookmark of bookmarks) {
      json += decodeURIComponent(new URL(bookmark.url).searchParams.get('d'));
    }

    return JSON.parse(json);
  }

  /**
   * @param {Partial<{create: boolean}>} extras
   * @returns {Promise<BrowserBookmark>}
   */
  static async _getBookmarkLocation(extras = {}) {
    const create = extras?.create ?? false;
    const location = this.getBookmarkLocation();

    let folder = JSON.parse(JSON.stringify(await browser.bookmarks.getTree()));
    folder = folder[0].children.find(x => x.id === location[0]) ?? null;

    for (let i = 1; i < location.length; ++i) {
      const match = folder.children.find(x => x.title === location[i]) ?? null;

      if (match != null) {
        folder = match;
      } else if (create) {
        folder = await browser.bookmarks.create({
          type: 'folder',
          parentId: folder.id,
          title: location[i],
        });
      } else {
        return null;
      }

      if (!('children' in folder)) {
        folder.children = [];
      }
    }

    return folder;
  }

  /**
   * @param {string} url
   * @returns {Promise<BrowserBookmark>}
   */
  static async _createBookmark(i, url) {
    const folder = await this._getBookmarkLocation({create: true});
    return await browser.bookmarks.create({
      type: 'bookmark',
      parentId: folder.id,
      title: `${this._pluginID()}#${i + 1}`,
      url: url,
    });
  }

  /**
   * @param {Record<string, any>} opts
   * @returns {void}
   */
  static async _setBookmarkData(opts) {
    const urls = this._bookmarkURLs(opts);

    const bookmarks = await this._getBookmarks();

    let i = 0;
    while (i < urls.length) {
      const url = urls[i];
      const bookmark = bookmarks.shift();
      if (bookmark) {
        await browser.bookmarks.update(bookmark.id, {url});
      } else {
        await this._createBookmark(i, url);
      }

      i += 1;
    }

    while (bookmarks.length > 0) {
      await browser.bookmarks.remove(bookmarks.shift().id);
    }
  }

  static async _clearBookmarkData() {
    const bookmarks = await this._getBookmarks();
    while (bookmarks.length > 0) {
      await browser.bookmarks.remove(bookmarks.shift().id);
    }
  }
}