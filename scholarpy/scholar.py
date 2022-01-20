import pandas as pd
from scholarly import scholarly
import plotly.express as px


def search_author(name, return_list=False):

    search_query = scholarly.search_author(name)
    if not return_list:
        return next(search_query)
    else:
        return list(search_query)


def search_author_id(id):

    try:
        return scholarly.search_author_id(id)
    except Exception as e:
        print("Invalid scholar id: {}".format(id))
        return None


def get_author_list(name):

    authors = search_author(name, return_list=True)
    result = [
        f"{author['affiliation']} | {author['name']} | {author['scholar_id']}" for author in authors]
    result.sort()
    result = [
        f"{author.split(' | ')[1]} | {author.split(' | ')[2]} | {author.split(' | ')[0]}" for author in result]
    return result


def search_org(name):

    return scholarly.search_org(name)


def search_author_by_org(org_id, return_list=False):
    """Search authors by organization id.

    Args:
        org_id (str): Organization id. For example, 145051948357103924
        return_list (bool, optional): If True, return a list of authors.

    Returns:
        list: A list of authors.
    """
    search_query = scholarly.search_author_by_organization(org_id)
    if not return_list:
        return next(search_query)
    else:
        return list(search_query)


def get_author_record(name=None, id=None, sections=[], sortby="citedby", limit=0):
    """[summary]

    Args:
        name ([type], optional): [description]. Defaults to None.
        id ([type], optional): [description]. Defaults to None.
        sections (list, optional): The sections that the user wants filled for an Author object. This can be: ['basics', 'indices', 'counts', 'coauthors', 'publications', 'public_access']. Defaults to [].
        sortby (str, optional): [description]. Defaults to "citedby".
        limit (int, optional): [description]. Defaults to 0.

    Raises:
        ValueError: [description]

    Returns:
        [type]: [description]
    """
    if name is not None:
        author = search_author(name)
    elif id is not None:
        if "|" in id:
            id = id.split("|")[1].strip()
        author = search_author_id(id)
    else:
        raise ValueError("Either name or id must be specified.")

    result = scholarly.fill(author, sections=sections,
                            sortby=sortby, publication_limit=limit)
    return result


def get_author_pubs(name=None, id=None, record=None, sections=["publications"], sortby="citedby", limit=0, return_df=False):

    if record is None:
        pubs = get_author_record(
            name=name, id=id, sections=sections, sortby=sortby, limit=limit)["publications"]
    else:
        pubs = record["publications"]

    result = []

    for pub in pubs:
        if "bib" in pub:
            if "title" in pub['bib']:
                pub["title"] = pub["bib"]["title"]
            if "pub_year" in pub['bib']:
                pub["year"] = pub["bib"]["pub_year"]

        if "bib" in pub:
            pub.pop("bib")
        if "source" in pub:
            pub.pop("source")
        if "filled" in pub:
            pub.pop("filled")

        result.append(pub)

    if return_df:
        return pd.DataFrame(result)
    else:
        return result


def get_author_basics(name=None, id=None, record=None, return_df=False):

    if record is None and (name is not None or id is not None):
        record = get_author_record(name=name, id=id)
    elif record is not None:
        pass
    else:
        raise ValueError("Either name or id must be specified.")

    items = ["name", "scholar_id", "affiliation", "affiliation_id", "scholar_url",
             "url_picture", "homepage", "email_domain", "interests", "citedby", "citedby5y", "hindex", "hindex5y", "i10index", "i10index5y", "cites_per_year"]

    result = {}
    for item in items:
        if item in record:
            result[item] = record[item]
        else:
            result[item] = ""
    if "organization" in record:
        result["affiliation_id"] = record["organization"]
    result["scholar_url"] = f"https://scholar.google.com/citations?user={record['scholar_id']}"

    if return_df:
        df = pd.DataFrame([result]).transpose()
        df.reset_index(inplace=True)
        df.columns = ["key", "value"]
        return df
    else:
        return result


def author_pubs_by_year(name=None, id=None, record=None, return_plot=False):

    pubs = get_author_pubs(name=name, id=id, record=record, return_df=True)
    stats = pubs.groupby("year").size()
    df = pd.DataFrame({"pubs": stats})
    df.reset_index(inplace=True)

    if not return_plot:
        return df
    else:
        fig = px.bar(df, x="year", y="pubs",
                     title=f"Publications by year")
        return df, fig


def author_citations_by_year(name=None, id=None, record=None, return_plot=False):

    if record is None and (name is not None or id is not None):
        record = get_author_record(name=name, id=id)
    elif record is not None:
        pass
    else:
        raise ValueError("Either name or id must be specified.")

    citations = record["cites_per_year"]
    df = pd.DataFrame(
        {"year": citations.keys(), "citations": citations.values()})

    if not return_plot:
        return df
    else:
        fig = px.bar(df, x="year", y="citations",
                     title=f"Citations by year")
        return df, fig


def get_author_coauthors(name=None, id=None, record=None, return_df=False):

    if record is None and (name is not None or id is not None):
        record = get_author_record(name=name, id=id)
    elif record is not None:
        pass
    else:
        raise ValueError("Either name or id must be specified.")

    coauthors = record["coauthors"]

    if not return_df:
        return coauthors
    else:
        df = pd.DataFrame(coauthors)
        df = df[["name", "scholar_id", "affiliation"]]
        return df
