"""Main module."""

import os
import dimcli
import leafmap
import webbrowser
import pandas as pd
import plotly.express as px


class Dsl(dimcli.Dsl):
    def __init__(self, key=None, **kwargs):
        """Initialize the DSL."""
        if key is None:
            key = os.environ.get("DIM_TOKEN")
            if key is None:
                webbrowser.open("https://api-lab.dimensions.ai")
                raise ValueError(
                    "No Dimensions API key can be found. Please go to https://www.dimensions.ai/contact-us to request an API key."
                )
            dimcli.login(key=key)

        super().__init__(**kwargs)

    def search_researcher_by_id(self, id, limit=1000, return_df=True):
        """Search a researcher by ID. For example, ur.010551261751.12"""
        # query = f'search researchers where id="{id}" return researchers[id+first_name+last_name+current_research_org+research_orgs+total_grants+total_publications+first_publication_year+last_publication_year+orcid_id+dimensions_url] limit {limit}'
        query = f'search researchers where id="{id}" return researchers[basics+extras] limit {limit}'
        result = self.query(query)
        if return_df:
            df2 = result.as_dataframe().transpose()
            df3 = pd.DataFrame(
                {"index": df2.index.tolist(), "value": df2.values.tolist()}
            )
            return df3
        else:
            return self.query(query)

    def search_researcher_by_name(self, name, limit=1000, return_list=False):
        """Search a researcher by name."""
        query = f'search researchers for "\\"{name}\\"" return researchers[basics+extras+obsolete] limit {limit}'
        result = self.query(query)
        if return_list:
            df = result.as_dataframe()
            if not df.empty:
                df = df[df["obsolete"] == 0]
                df["current_research_org_name"] = df["current_research_org.name"]
                if not df.empty:
                    items = []
                    for row in df.itertuples():
                        item = (
                            str(row.first_name)
                            + " "
                            + str(row.last_name)
                            + " | "
                            + str(row.id)
                            + " | "
                            + str(row.current_research_org_name)
                        )
                        items.append(item)

                    return result, items
            else:
                return result, None
        else:
            return result

    def search_journal_by_id(self, id, limit=1000):
        """Search a journal by ID.

        Args:
            id (str): The ID of the journal. For example, jour.1018957
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            [type]: [description]
        """

        query = (
            f'search source_titles where id="{id}" return source_titles limit {limit}'
        )
        return self.query(query)

    def search_journal_by_title(self, title, limit=1000, exact_match=True):
        """Search a journal by title."""
        query = f'search source_titles for "{title}" return source_titles limit {limit}'
        result = self.query(query)
        try:
            if exact_match:
                df = result.as_dataframe()
                sub_df = df[df["title"].str.lower() == title.lower()]
                journal_id = sub_df["id"].values.tolist()[0]
                query = f'search source_titles where id="{journal_id}" return source_titles limit {limit}'
                return self.query(query)

            else:
                return result
        except Exception as e:
            print("No journal found.")
            return None

    def search_organization_by_id(self, id, limit=1000):
        """Search an organization by ID. For example, grid.411461.7

        Args:
            id (str): The ID of the organization. For example, org.010551261751.12
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            [type]: [description]
        """
        query = (
            f'search organizations where id="{id}" return organizations limit {limit}'
        )
        return self.query(query)

    def search_organization_by_name(self, name, limit=1000):
        """Search an organization by name."""
        query = f'search organizations for "\\"{name}\\"" return organizations limit {limit}'
        return self.query(query)

    def get_pubs_by_researcher_id(self, id, limit=1000, extra=False):
        """Search a publication by researcher ID. For example, ur.010551261751.12

        Args:
            id (str): The ID of the publication. For example, pub.010551261751.12
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            [type]: [description]
        """
        extra_str = ""
        if extra:
            extra_str = "[basics+authors_count+times_cited+dimensions_url]"
        query = f'search publications where researchers.id="{id}" return publications{extra_str} limit {limit}'
        return self.query(query)

    def get_pubs_by_journal_id(self, id, start_year=None, end_year=None, limit=1000):
        """Search a publication by journal ID. For example, jour.1018957

        Args:
            id (str): The ID of the publication. For example, pub.010551261751.12
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            [type]: [description]
        """
        if (start_year is not None) and (end_year is not None):
            query = f'search publications where journal.id="{id}" and year>={start_year} and year<={end_year} return publications limit {limit}'
        elif start_year is not None:
            query = f'search publications where journal.id="{id}" and year>={start_year} return publications limit {limit}'
        elif end_year is not None:
            query = f'search publications where journal.id="{id}" and year<={end_year} return publications limit {limit}'
        else:
            query = f'search publications where journal.id="{id}" return publications limit {limit}'
        # query = f'search publications where journal.id="{id}" return publications limit {limit}'
        return self.query(query)

    def get_pubs_by_organization_id(
        self, id, start_year=None, end_year=None, limit=1000
    ):
        """Search a publication by organization ID. For example, grid.411461.7

        Args:
            id (str): The ID of the publication. For example, pub.010551261751.12
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            [type]: [description]
        """
        if not isinstance(start_year, int) and start_year is not None:
            raise TypeError("start_year must be an integer.")
        if not isinstance(end_year, int) and end_year is not None:
            raise TypeError("end_year must be an integer.")

        years = None
        if start_year is not None and end_year is not None:
            if start_year > end_year:
                raise ValueError("start_year must be less than end_year.")
            else:
                years = f"[{start_year}:{end_year}]"

        if years is None:
            query = f'search publications where research_orgs="{id}" return publications limit {limit}'
        else:
            query = f'search publications where year in {years} and research_orgs="{id}" return publications limit {limit}'

        print(query)

        return self.query(query)

    def h_index(self, id, limit=1000):
        def the_H_function(sorted_citations_list, n=1):
            """from a list of integers [n1, n2 ..] representing publications citations,
            return the max list-position which is >= integer

            eg
            >>> the_H_function([10, 8, 5, 4, 3]) => 4
            >>> the_H_function([25, 8, 5, 3, 3]) => 3
            >>> the_H_function([1000, 20]) => 2
            """
            if sorted_citations_list and sorted_citations_list[0] >= n:
                return the_H_function(sorted_citations_list[1:], n + 1)
            else:
                return n - 1

        def get_pubs_citations(researcher_id):
            q = """search publications where researchers.id = "{}" return publications[times_cited] sort by times_cited limit {}"""
            pubs = self.query(q.format(researcher_id, limit))
            return list(pubs.as_dataframe().fillna(0)["times_cited"])

        return the_H_function(get_pubs_citations(id))

    def researcher_pubs_stats(
        self, id, col="year", limit=1000, return_plot=False, **kwargs
    ):
        """Return researcher publications stats.

        Args:
            id (str): The ID of the publication. For example, pub.010551261751.12
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            [type]: [description]
        """
        result = self.get_pubs_by_researcher_id(id, limit)
        pubs = result.as_dataframe()
        df = pubs[col].value_counts().sort_index()
        df2 = pd.DataFrame({"year": df.index, "citations": df.values})
        if return_plot:
            return df.plot.bar(**kwargs)
        else:
            return df2

    def researcher_pubs_authors(self, id, limit=1000):
        """Return researcher publications authors.

        Args:
            id (str): The ID of the publication. For example, pub.010551261751.12
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            [type]: [description]
        """
        result = self.get_pubs_by_researcher_id(id, limit)
        pubs = result.as_dataframe()
        authors = result.as_dataframe_authors()["pub_id"].value_counts()
        df2 = pd.DataFrame({"id": authors.index, "authors": authors.values})
        df = pubs.join(df2.set_index("id"), on="id")
        return df

    def search_pubs_by_keywords(
        self,
        keywords,
        scope="title_abstract_only",
        fields=None,
        sorted_key="times_cited",
        limit=1000,
    ):
        """Search publications by keyword.

        Args:
            keywords (str): The keyword to search.
            scope (str, optional): The scope of the search. Can be one of ["authors", "concepts", "full_data", "full_data_exact", "title_abstract_only", "title_only"]. Defaults to "title_abstract_only".
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            [type]: [description]
        """

        allowed_scopes = [
            "authors",
            "concepts",
            "full_data",
            "full_data_exact",
            "title_abstract_only",
            "title_only",
        ]

        if fields is None:
            fields = "basics+altmetric+times_cited+field_citation_ratio+authors_count+doi+dimensions_url"

        if scope not in allowed_scopes:
            raise ValueError(f"scope must be one of {allowed_scopes}")
        query = f'search publications in {scope} for "\\"{keywords}\\"" return publications[{fields}] sort by {sorted_key} limit {limit}'
        return self.query(query)

    def researcher_annual_stats(self, data, geonames_df=None):

        pubs = data.as_dataframe()
        years_dict = pubs[["id", "year"]].set_index("id").to_dict()["year"]
        df = data.as_dataframe_authors()
        df["name"] = df["first_name"] + " " + df["last_name"]
        affiliations = df["affiliations"].values.tolist()

        institutions = []
        city_ids = []
        years = []
        cities = []
        countries = []
        latitudes = []
        longitudes = []

        ids = df["pub_id"].values.tolist()
        for index, a in enumerate(affiliations):
            try:
                institution = a[0]["name"]
                institutions.append(institution)
            except:
                institutions.append("")

            try:
                city_id = a[0]["city_id"]
                city_ids.append(city_id)
            except:
                city_ids.append(0)

            try:
                city = a[0]["city"]
                cities.append(city)
            except:
                cities.append("")

            try:
                country = a[0]["country"]
                countries.append(country)
            except:
                countries.append("")

            if geonames_df is not None:
                try:
                    latitude, longitude = geoname_latlon(city_ids[-1], geonames_df)
                    latitudes.append(latitude)
                    longitudes.append(longitude)
                except:
                    latitudes.append(0)
                    longitudes.append(0)

            years.append((years_dict[ids[index]]))

        df["year"] = years
        df["institution"] = institutions
        df["city"] = cities
        df["country"] = countries
        df["city_id"] = city_ids

        if geonames_df is not None:
            df["latitude"] = latitudes
            df["longitude"] = longitudes

        pubs_stats = pubs.groupby("year").size()
        collaborators_stats = (
            df.groupby(["year", "name"]).size().groupby(level=0).size()
        )
        institutions_stats = (
            df.groupby(["year", "institution"]).size().groupby(level=0).size()
        )
        cities_stats = df.groupby(["year", "city_id"]).size().groupby(level=0).size()

        df2 = pd.DataFrame(
            {
                "year": cities_stats.index,
                "pubs": pubs_stats,
                "collaborators": collaborators_stats,
                "institutions": institutions_stats,
                "cities": cities_stats,
            }
        )
        if geonames_df is None:
            return df2
        else:
            return (
                df2,
                df[
                    [
                        "name",
                        "year",
                        "institution",
                        "city",
                        "country",
                        "latitude",
                        "longitude",
                    ]
                ],
            )


def get_geonames(**kwargs):

    url = "https://raw.githubusercontent.com/giswqs/data/main/world/cities5000.csv"
    # columns = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature_class', 'feature_code', 'country_code',
    #            'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation', 'dem', 'timezone', 'modification_date']
    df = pd.read_csv(url, sep="\t", encoding="utf-8")

    if "columns" in kwargs and isinstance(kwargs["columns"], list):
        df = df[kwargs["columns"]]
    else:
        df = df[
            ["geonameid", "name", "country_code", "population", "latitude", "longitude"]
        ]

    return df


def geoname_latlon(id, df=None):

    if not isinstance(id, int):
        try:
            id = int(id)
        except:
            raise ValueError("id must be an integer")

    if df is None:
        df = get_geonames()

    row = df[df["geonameid"] == id]
    lat = 0
    lon = 0
    if not row.empty:
        lat = row.iloc[0]["latitude"]
        lon = row.iloc[0]["longitude"]

    return lat, lon


def collaborator_locations(df):

    if "name" in df.columns:
        df.drop(columns=["name"], axis=1, inplace=True)

    if "year" in df.columns:
        df.drop(columns=["year"], axis=1, inplace=True)

    if "index" in df.columns:
        df.drop(columns=["index"], axis=1, inplace=True)

    df.drop_duplicates(inplace=True)
    df = df[df["latitude"] != 0].reset_index()
    df.drop(columns=["index"], axis=1, inplace=True)

    return df


def annual_stats_barplot(df, columns=None, **kwargs):

    if columns is None:
        columns = ["pubs", "collaborators", "institutions", "cities"]
    fig = px.bar(
        df,
        x="year",
        y=columns,
        barmode="group",
    )
    return fig


def json_to_df(json_data, transpose=False):
    df = json_data.as_dataframe()
    if not df.empty:
        if transpose:
            df = df.transpose()

        out_csv = leafmap.temp_file_path(".csv")
        df.to_csv(out_csv, index=transpose)
        df = pd.read_csv(out_csv)
        os.remove(out_csv)
        return df
    else:
        return None
