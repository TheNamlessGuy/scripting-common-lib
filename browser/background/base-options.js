class BaseOptions {
  constructor() { throw Error(`${this.constructor.name} is abstract`); }

  /**
   * @returns {Record<string, any>}
   */
  static async get() {
    // TODO: Should change to "is local storage empty? Check if we have access to bookmarks, and if we do, check if we have any bookmark data"
    // if (this._saveUsingBookmark) {
    //   return await this._getBookmarkData();
    // }

    return await browser.storage.local.get();
  }

  /**
   * @param {Record<string, any>} opts
   * @param {Partial<{saveUsingBookmark: boolean}>} extras
   */
  static async set(opts, extras = {}) {
    const saveUsingBookmark = extras?.saveUsingBookmark ?? false;

    if (saveUsingBookmark) {
      await this._setBookmarkData(opts);
      await browser.storage.local.clear();
    } else {
      await browser.storage.local.clear();
      await browser.storage.local.set(opts);
    }
  }

  /**
   * @returns {string[]}
   */
  static getBookmarkLocation() {
    return ['menu________', 'Plugin data', this._pluginID()];
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
   * @param {Record<string, any>} opts
   * @returns {string[]}
   */
  static _bookmarkURLs(opts) {
    const url = this._baseBookmarkURL();

    const optsStr = encodeURIComponent(JSON.stringify(opts));
    const chunks = []; // TODO: Chunk optsStr so that the bookmark URL length won't exceed limits

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
    return (await browser.bookmarks.search({query: prefix})).filter(x => x.startsWith(prefix));
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
      json += new URL(bookmark.url).searchParams.get('data');
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
        folder = await browser.bookmark.create({
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
    bookmarks.sort((a, b) => {
      const ai = parseInt(new URL(a.url).searchParams.get('i'));
      const bi = parseInt(new URL(b.url).searchParams.get('i'));
      return ai - bi;
    });

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
}