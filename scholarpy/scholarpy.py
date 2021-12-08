"""Main module."""

import os
import dimcli
import webbrowser
import pandas as pd


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

    def search_researcher_by_name(self, name, limit=1000):
        """Search a researcher by name."""
        query = (
            f'search researchers for "\\"{name}\\"" return researchers limit {limit}'
        )
        return self.query(query)

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
            extra_str = "[basics+authors_count+times_cited]"
        query = f'search publications where researchers.id="{id}" return publications{extra_str} limit {limit}'
        return self.query(query)

    def get_pubs_by_journal_id(self, id, limit=1000):
        """Search a publication by journal ID. For example, jour.1018957

        Args:
            id (str): The ID of the publication. For example, pub.010551261751.12
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            [type]: [description]
        """
        query = f'search publications where journal.id="{id}" return publications limit {limit}'
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

    def search_pubs_by_keyword(
        self, keyword, scope="title_abstract_only", sorted_key="times_cited", limit=1000
    ):
        """Search publications by keyword.

        Args:
            keyword (str): The keyword to search.
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
        if scope not in allowed_scopes:
            raise ValueError(f"scope must be one of {allowed_scopes}")
        query = f'search publications in {scope} for "\\"{keyword}\\"" return publications[id+journal+type+title+authors+year+volume+issue+pages+doi+dimensions_url+times_cited] sort by {sorted_key} limit {limit}'
        return self.query(query)

    def researcher_annual_stats(self, data):

        pubs = data.as_dataframe()
        years_dict = pubs[["id", "year"]].set_index("id").to_dict()["year"]
        df = data.as_dataframe_authors()
        df["name"] = df["first_name"] + " " + df["last_name"]
        affiliations = df["affiliations"].values.tolist()

        institutions = []
        cities = []
        years = []

        ids = df["pub_id"].values.tolist()
        for index, a in enumerate(affiliations):
            try:
                institution = a[0]["name"]
                institutions.append(institution)
            except:
                institutions.append("")

            try:
                city = a[0]["city_id"]
                cities.append(city)
            except:
                cities.append(0)
            years.append((years_dict[ids[index]]))

        df["institution"] = institutions
        df["city_id"] = cities
        df["year"] = years

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
        return df2
