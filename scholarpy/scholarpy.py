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

    def search_researcher_by_id(
        self,
        id,
        fields=None,
        iterative=False,
        limit=1000,
        return_df=False,
        **kwargs,
    ):
        """Search a researcher by ID.

        Args:
            id (str): The ID of the researcher. For example, ur.010551261751.12
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.
            return_df (bool, optional): If True, the results will be returned as a dataframe. Defaults to False.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """
        """Search a researcher by a Dimensions Research ID. For example, ur.010551261751.12"""

        if fields is None:
            fields = "[basics+extras]"

        query = f'search researchers where id="{id}" return researchers{fields}'

        if iterative:
            result = self.query_iterative(query, limit=limit, **kwargs)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)
        if return_df:
            df2 = result.as_dataframe().transpose()
            df3 = pd.DataFrame(
                {"index": df2.index.tolist(), "value": df2.values.tolist()}
            )
            df3["value"] = df3["value"]
            print(type(df3["value"]))
            return df3
        else:
            return result

    def search_researcher_by_name(
        self,
        name,
        fields=None,
        iterative=False,
        limit=1000,
        return_list=False,
        **kwargs,
    ):
        """Search a researcher by name.

        Args:
            name (str): The name of the researcher.
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.
            return_list (bool, optional): If True, the results will be returned as a list. Defaults to False.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """

        if fields is None:
            fields = "[basics+extras]"

        query = f'search researchers for "\\"{name}\\"" where obsolete=0 and total_publications>0 return researchers{fields}'
        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        if return_list:
            df = result.as_dataframe()
            if not df.empty:
                # df.sort_values(by=["id"], inplace=True)
                df["current_research_org_name"] = df["current_research_org.name"]
                df.sort_values("current_research_org_name", inplace=True)
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

    def search_researcher_collaborators(self, id, pubs=None):
        """Search collaborators of a researcher.

        Args:
            id (str): The ID of the researcher. For example, ur.010551261751.12
            pubs (dimcli.DslDataset, optional): The publications of the researcher. Defaults to None.
        Returns:
            pd.DataFrame: A dataframe of the collaborators.
        """
        if pubs is None:
            pubs = self.search_pubs_by_researcher_id(id)
        df = pubs.as_dataframe_authors()
        df = df[df["researcher_id"] != id]
        df["Name"] = df["first_name"].str.split(
            " ").str[0] + " " + df["last_name"]
        names = df.drop_duplicates("Name").copy()
        affiliations = names["affiliations"].values.tolist()
        institutions = []
        for a in enumerate(affiliations):
            try:
                institution = a[1][0]["name"]
                institutions.append(institution)
            except:
                institutions.append("")

        names["Institution"] = institutions
        names = names[["Name", "Institution"]]

        result = pd.DataFrame(df["Name"].value_counts())
        result = pd.DataFrame(
            {"Name": result.index, "Count": result["Name"].values})
        return result.merge(names, on="Name")

    def search_orcid_by_name(
        self,
        name,
        fields=None,
        iterative=False,
        limit=1000,
        return_list=False,
        **kwargs,
    ):
        """Search a researcher orcid by name.

        Args:
            name (str): The name of the researcher.
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.
            return_list (bool, optional): If True, the results will be returned as a list. Defaults to False.

        Returns:
            pd.DataFrame: A dataframe of the results.
        """

        result = self.search_researcher_by_name(
            name, fields=fields, iterative=iterative, limit=limit, return_list=False
        )
        df = result.as_dataframe()
        if "orcid_id" in df.columns:
            df = df[~df["orcid_id"].isnull()]
            ids = [id[0] for id in df["orcid_id"].values.tolist()]
            df["orcid_id"] = ids
            # df.sort_values(by=["orcid_id"], inplace=True)
            df["current_research_org_name"] = df["current_research_org.name"]
            df.sort_values("current_research_org_name", inplace=True)
            if return_list:
                df["uid"] = (
                    df["first_name"]
                    + " "
                    + df["last_name"]
                    + " | "
                    + df["orcid_id"]
                    + " | "
                    + df["current_research_org.name"]
                )
                df = df[~df["uid"].isnull()]
                return df["uid"].tolist()
            else:
                return df
        else:
            return None

    def search_journal_by_id(self, id, fields=None, **kwargs):
        """Search a journal by ID.

        Args:
            id (str): The ID of the journal. For example, jour.1018957
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """

        if fields is None:
            fields = ""
        query = f'search source_titles where id="{id}" return source_titles{fields}'
        return self.query(query)

    def search_journal_by_title(
        self,
        title,
        exact_match=True,
        fields=None,
        iterative=False,
        limit=1000,
        **kwargs,
    ):
        """Search a journal by title.

        Args:
            title (str): The title of the journal.
            exact_match (bool, optional): If True, the title must be an exact match. Defaults to True.
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """
        if fields is None:
            fields = ""
        query = f'search source_titles for "{title}" return source_titles{fields}'

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        try:
            if exact_match:
                df = result.as_dataframe()
                sub_df = df[df["title"].str.lower() == title.lower()]
                journal_id = sub_df["id"].values.tolist()[0]
                query = f'search source_titles where id="{journal_id}" return source_titles{fields}'
                return self.query(query)

            else:
                return result
        except Exception as e:
            print("No journal can be found.")
            return None

    def search_org_by_id(self, id, fields=None, **kwargs):
        """Search an organization by ID. For example, grid.411461.7

        Args:
            id (str): The ID of the organization. For example, org.010551261751.12
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """
        if fields is None:
            fields = ""
        query = f'search organizations where id="{id}" return organizations{fields}'
        return self.query(query)

    def search_org_by_name(
        self, name, exact_match=True, fields=None, iterative=False, limit=1000, return_list=False, **kwargs
    ):
        """Search an organization by name.

        Args:
            name (str): The name of the organization.
            exact_match (bool, optional): If True, the name must be an exact match. Defaults to True.
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.
            return_list (bool, optional): If True, the results will be returned as a list. Defaults to False.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """
        if fields is None:
            fields = ""
        query = f'search organizations for "\\"{name}\\"" return organizations{fields}'
        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        try:
            if exact_match:
                df = result.as_dataframe()
                sub_df = df[df["name"].str.lower() == name.lower()]
                org_id = sub_df["id"].values.tolist()[0]
                query = f'search organizations where id="{org_id}" return organizations{fields}'
                result = self.query(query)

            if return_list:

                df = result.as_dataframe()
                if not df.empty:
                    df.sort_values("name", inplace=True)
                    df["name_id"] = df["id"] + " | " + df["name"]
                    orgs = df["name_id"].values.tolist()
                    return orgs
                else:
                    return None
            else:
                return result

        except Exception as e:
            print("No organization can be found.")
            return None

    def search_pubs_by_researcher_id(
        self,
        id,
        start_year=None,
        end_year=None,
        fields=None,
        iterative=False,
        limit=1000,
        **kwargs,
    ):
        """Search publications by researcher ID.

        Args:
            id (str): The ID of the researcher. For example, res.010551261751.12
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """
        if fields is None:
            fields = "[basics+authors_count+times_cited+dimensions_url]"

        if (start_year is not None) and (end_year is not None):
            query = f'search publications where researchers.id="{id}" and year>={start_year} and year<={end_year} return publications{fields}'
        elif start_year is not None:
            query = f'search publications where researchers.id="{id}" and year>={start_year} return publications{fields}'
        elif end_year is not None:
            query = f'search publications where researchers.id="{id}" and year<={end_year} return publications{fields}'
        else:
            query = f'search publications where researchers.id="{id}" return publications{fields}'

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        return result

    def search_pubs_by_journal_id(
        self,
        id,
        start_year=None,
        end_year=None,
        fields=None,
        iterative=False,
        limit=1000,
        **kwargs,
    ):
        """Search publications by journal ID.

        Args:
            id (str): The ID of the journal. For example, jour.1018957
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """
        if fields is None:
            fields = ""

        if (start_year is not None) and (end_year is not None):
            query = f'search publications where journal.id="{id}" and year>={start_year} and year<={end_year} return publications{fields}'
        elif start_year is not None:
            query = f'search publications where journal.id="{id}" and year>={start_year} return publications{fields}'
        elif end_year is not None:
            query = f'search publications where journal.id="{id}" and year<={end_year} return publications{fields}'
        else:
            query = f'search publications where journal.id="{id}" return publications{fields}'

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        return result

    def search_pubs_by_org_id(
        self,
        id,
        start_year=None,
        end_year=None,
        fields=None,
        iterative=False,
        limit=1000,
        **kwargs,
    ):
        """Search publications by organization ID.

        Args:
            id (str): The ID of the organization. For example, grid.411461.7
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """
        if fields is None:
            fields = ""

        if (start_year is not None) and (end_year is not None):
            query = f'search publications where research_orgs="{id}" and year>={start_year} and year<={end_year} return publications{fields}'
        elif start_year is not None:
            query = f'search publications where research_orgs="{id}" and year>={start_year} return publications{fields}'
        elif end_year is not None:
            query = f'search publications where research_orgs="{id}" and year<={end_year} return publications{fields}'
        else:
            query = f'search publications where research_orgs="{id}" return publications{fields}'

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        return result

    def search_pubs_by_keyword(
        self,
        keyword,
        exact_match=True,
        scope="title_abstract_only",
        start_year=None,
        end_year=None,
        journal_id=None,
        fields=None,
        sorted_field="times_cited",
        iterative=False,
        limit=1000,
        **kwargs,
    ):
        """Search publications by keyword.

        Args:
            keyword (str): The keyword to search.
            exact_match (bool, optional): If True, the keyword will be matched exactly. Defaults to True.
            scope (str, optional): The scope of the search. Defaults to "title_abstract_only".
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            fields (str, optional): The fields to return. For example, [basics+extras]. Defaults to None.
            sorted_field (str, optional): The field to sort by. Defaults to "times_cited".
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.

        Raises:
            ValueError: [description]

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """
        if exact_match:
            exact = '\\"'
        else:
            exact = ""

        if journal_id is not None:
            journal = f'and journal.id="{journal_id}"'
        else:
            journal = ""

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

        if fields is None:
            fields = "[basics+altmetric+times_cited+field_citation_ratio+authors_count+doi+dimensions_url]"

        if (start_year is not None) and (end_year is not None):
            query = f'search publications in {scope} for "{exact}{keyword}{exact}" where year>={start_year} and year<={end_year} {journal} return publications{fields} sort by {sorted_field}'
        elif start_year is not None:
            query = f'search publications in {scope} for "{exact}{keyword}{exact}" where year>={start_year} {journal} return publications{fields} sort by {sorted_field}'
        elif end_year is not None:
            query = f'search publications in {scope} for "{exact}{keyword}{exact}" where year<={end_year} {journal} return publications{fields} sort by {sorted_field}'
        else:
            if journal_id is not None:
                journal = f'where journal.id="{journal_id}"'
            else:
                journal = ""
            query = f'search publications in {scope} for "{exact}{keyword}{exact}" {journal} return publications{fields} sort by {sorted_field}'

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        return result

    def search_grants_by_keyword(
        self,
        keyword,
        exact_match=True,
        scope="title_only",
        start_year=None,
        end_year=None,
        fields=None,
        sorted_field="start_year",
        iterative=False,
        limit=1000,
        **kwargs,
    ):

        if exact_match:
            exact = '\\"'
        else:
            exact = ""

        allowed_scopes = [
            "concepts",
            "full_data",
            "investigators",
            "title_abstract_only",
            "title_only",
        ]

        if scope not in allowed_scopes:
            raise ValueError(f"scope must be one of {allowed_scopes}")

        if fields is None:
            fields = "[basics+extras+dimensions_url]"

        if end_year is not None:
            end_year = str(end_year)
            if len(str(end_year)) != 4:
                raise ValueError("end_year must be a 4-digit number")
            else:
                end_year = str(end_year) + "-12-31"

        if (start_year is not None) and (end_year is not None):
            query = f'search grants in {scope} for "{exact}{keyword}{exact}" where start_year>={start_year} and end_date<="{end_year}" return grants{fields} sort by {sorted_field}'
        elif start_year is not None:
            query = f'search grants in {scope} for "{exact}{keyword}{exact}" where start_year>={start_year} return grants{fields} sort by {sorted_field}'
        elif end_year is not None:
            query = f'search grants in {scope} for "{exact}{keyword}{exact}" where end_date<="{end_year}" return grants{fields} sort by {sorted_field}'
        else:
            query = f'search grants in {scope} for "{exact}{keyword}{exact}" return grants{fields} sort by {sorted_field}'

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        return result

    def h_index(self, id, iterative=False, limit=1000):
        """Get the h-index of a researcher.

        Args:
            id (str): The ID of the researcher. For example, res.010551261751.12
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.
        """

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

        def get_pubs_citations(researcher_id, iterative=False, limit=1000):
            q = f'search publications where researchers.id = "{researcher_id}" return publications[times_cited] sort by times_cited'

            if iterative:
                result = self.query_iterative(q, limit=limit)
            else:
                q = f"{q} limit {limit}"
                result = self.query(q)

            return list(result.as_dataframe().fillna(0)["times_cited"])

        return the_H_function(get_pubs_citations(id, iterative=iterative, limit=limit))

    def researcher_pubs_stats(
        self,
        id,
        start_year=None,
        end_year=None,
        iterative=False,
        limit=1000,
        return_plot=False,
        **kwargs,
    ):
        """Get the publications stats of a researcher.

        Args:
            id (str): The ID of the researcher. For example, ur.010551261751.12
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.
            return_plot (bool, optional): If True, the plot will be returned. Defaults to False.

        Returns:
            pandas.DataFrame: The dataframe of the results.
        """

        result = self.search_pubs_by_researcher_id(
            id, start_year, end_year, iterative=iterative, limit=limit
        )
        pubs = result.as_dataframe()
        df = pubs["year"].value_counts().sort_index()
        df2 = pd.DataFrame({"year": df.index, "citations": df.values})
        if return_plot:
            return df.plot.bar(**kwargs)
        else:
            return df2

    def researcher_pubs_authors(
        self, id, start_year=None, end_year=None, iterative=False, limit=1000
    ):
        """Get the authors of a researcher's publications.

        Args:
            id (str): The ID of the researcher. For example, ur.010551261751.12
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            pandas.DataFrame: The dataframe of the results.
        """

        result = self.search_pubs_by_researcher_id(
            id, start_year, end_year, iterative=iterative, limit=limit
        )
        pubs = result.as_dataframe()
        authors = result.as_dataframe_authors()["pub_id"].value_counts()
        df2 = pd.DataFrame({"id": authors.index, "authors": authors.values})
        df = pubs.join(df2.set_index("id"), on="id")
        return df

    def researcher_annual_stats(self, data, geonames_df=None):
        """Get the annual stats of a researcher, including publications, collaborators, collaborating institutions, and cities.

        Args:
            data (dimcli.DslDataset): JSON data of the input. It can be derived from search_pubs_by_researcher_id().
            geonames_df (pd.DataFrame, optional): The geonames dataframe. Defaults to None.

        Returns:
            pd.DataFrame: The dataframe of the results.
        """
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
                    latitude, longitude = geoname_latlon(
                        city_ids[-1], geonames_df)
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
        cities_stats = df.groupby(
            ["year", "city_id"]).size().groupby(level=0).size()

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

    def org_pubs_annual_stats(self, org_id, start_year=None, end_year=None, iterative=False, limit=1000, return_plot=False, **kwargs):
        """Search publications by organization ID.

        Args:
            org_id (str): The ID of the organization. For example, grid.411461.7
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.
            return_plot (bool, optional): If True, the plot of the results will be returned. Defaults to False.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """

        if (start_year is not None) and (end_year is not None):
            query = f'search publications where research_orgs="{org_id}" and year>={start_year} and year<={end_year} return year'
        elif start_year is not None:
            query = f'search publications where research_orgs="{org_id}" and year>={start_year} return year'
        elif end_year is not None:
            query = f'search publications where research_orgs="{org_id}" and year<={end_year} return year'
        else:
            query = f'search publications where research_orgs="{org_id}" return year'

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        df = result.as_dataframe()
        df.rename(columns={"id": "year"}, inplace=True)

        if not return_plot:
            return df
        else:
            if not df.empty:
                org_name = self.search_org_by_id(
                    org_id).as_dataframe()["name"][0]
                fig = px.bar(df, x="year", y="count",
                             title=f"Publications from {org_name} - by year")
                return df, fig
            else:
                return df, None

    def org_grants_annual_stats(self, org_id, start_year=None, end_year=None, iterative=False, limit=100, return_plot=False, **kwargs):
        """Search publications by organization ID.

        Args:
            org_id (str): The ID of the organization. For example, grid.411461.7
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.
            return_plot (bool, optional): If True, the plot of the results will be returned. Defaults to False.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """

        if (start_year is not None) and (end_year is not None):
            # query = f'search grants where research_orgs="{org_id}" and start_year>={start_year} and end_date<="{end_year}-12-31" return start_year aggregate funding'
            query = f'search grants where research_orgs="{org_id}" and start_year>={start_year} return start_year aggregate funding'
        elif start_year is not None:
            query = f'search grants where research_orgs="{org_id}" and start_year>={start_year} return start_year aggregate funding'
        elif end_year is not None:
            query = f'search grants where research_orgs="{org_id}" return start_year aggregate funding'
        else:
            query = f'search grants where research_orgs="{org_id}" return start_year aggregate funding'

        # if limit is None and start_year is not None and end_year is not None:
        #     limit = end_year - start_year + 1
        # else:
        #     limit = 30

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        df = result.as_dataframe()
        df.rename(columns={"id": "year"}, inplace=True)

        if not return_plot:
            return df
        else:
            if not df.empty:
                org_name = self.search_org_by_id(
                    org_id).as_dataframe()["name"][0]
                fig_count = px.bar(df, x="year", y="count",
                                   title=f"The number of grants for {org_name} - by year")
                fig_amount = px.bar(df, x="year", y="funding",
                                    title=f"The funding amount for {org_name} - by year")

                return df, fig_count, fig_amount
            else:
                return df, None, None

    def org_grant_funders(self, org_id, start_year=None, end_year=None, iterative=False, limit=20, return_plot=False, **kwargs):
        """Top funders of an organization.

        Args:
            org_id (str): The ID of the organization. For example, grid.411461.7
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 20.
            return_plot (bool, optional): If True, the plot of the results will be returned. Defaults to False.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """

        if (start_year is not None) and (end_year is not None):
            query = f'search grants where research_orgs="{org_id}" and year>={start_year} and year<={end_year} return funders aggregate funding sort by funding'
        elif start_year is not None:
            query = f'search grants where research_orgs="{org_id}" and year>={start_year} return funders aggregate funding sort by funding'
        elif end_year is not None:
            query = f'search grants where research_orgs="{org_id}" and year<={end_year} return funders aggregate funding sort by funding'
        else:
            query = f'search grants where research_orgs="{org_id}" return funders aggregate funding sort by funding'

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        df = result.as_dataframe()
        if not return_plot:
            return df
        else:
            if not df.empty:
                org_name = self.search_org_by_id(
                    org_id).as_dataframe()["name"][0]
                fig = px.bar(df,
                             x="name", y="funding",
                             title=f"Funding for {org_name} - by funder")
                return df, fig
            else:
                return df, None

    def search_grants_by_org(self, org_id, start_year=None, end_year=None, iterative=False, limit=1000, **kwargs):
        """Search grants by organization id.

        Args:
            org_id (str): The ID of the organization. For example, grid.411461.7
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 20.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """

        if (start_year is not None) and (end_year is not None):
            query = f'search grants where research_orgs="{org_id}" and start_year>={start_year} return grants[basics+extras]'
        elif start_year is not None:
            query = f'search grants where research_orgs="{org_id}" and start_year>={start_year} return grants[basics+extras]'
        elif end_year is not None:
            query = f'search grants where research_orgs="{org_id}" and start_year<={end_year} return grants[basics+extras]'
        else:
            query = f'search grants where research_orgs="{org_id}" return grants[basics+extras]'

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        return result

    def search_grants_by_researcher(self, researcher_id, start_year=None, end_year=None, iterative=False, limit=1000, **kwargs):
        """Search grants by researcher id.

        Args:
            researcher_id (str): The ID of the research. For example, ur.01361677540.55
            start_year (int, optional): The start year of the publication. Defaults to None.
            end_year (int, optional): The end year of the publication. Defaults to None.
            iterative (bool, optional): If True, the query will be iterative. Defaults to False.
            limit (int, optional): The number of results to return. Defaults to 1000.

        Returns:
            dimcli.DslDataset: JSON data of the results.
        """

        if (start_year is not None) and (end_year is not None):
            query = f'search grants where researchers="{researcher_id}" and start_year>={start_year} return grants[basics+extras]'
        elif start_year is not None:
            query = f'search grants where researchers="{researcher_id}" and start_year>={start_year} return grants[basics+extras]'
        elif end_year is not None:
            query = f'search grants where researchers="{researcher_id}" and start_year<={end_year} return grants[basics+extras]'
        else:
            query = f'search grants where researchers="{researcher_id}" return grants[basics+extras]'

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        return result

    def org_pubs_most_cited(self, org_id, recent=False, iterative=False, limit=100, **kwargs):

        if recent:
            query = f"""search publications where research_orgs.id="{org_id}"
            return publications[basics+recent_citations]
            sort by recent_citations"""
        else:
            query = f"""search publications where research_orgs.id="{org_id}"
            return publications[basics+times_cited]
            sort by times_cited"""

        if iterative:
            result = self.query_iterative(query, limit=limit)
        else:
            query = f"{query} limit {limit}"
            result = self.query(query)

        return result

    def org_pubs_top_areas(self, org_id, iterative=False, limit=1000, return_plot=False, **kwargs):

            query = f"""search publications where research_orgs.id="{org_id}"
            return publications[doi+title+times_cited+category_for+journal]
            sort by times_cited"""

            if iterative:
                result = self.query_iterative(query, limit=limit)
            else:
                query = f"{query} limit {limit}"
                result = self.query(query)    

            raw_df = result.as_dataframe()
            dimcli.utils.normalize_key("category_for", result.publications, [])
            df = pd.json_normalize(result.publications, record_path='category_for', meta=['doi', 'title', 'times_cited', ], errors='ignore' )
            org_name = self.search_org_by_id(org_id).as_dataframe()["name"][0]
            if return_plot:
                area_fig = px.scatter(df,
                    x="times_cited", y="name",
                    marginal_x="histogram",
                    marginal_y="histogram",
                    hover_data=["doi", "title"],
                    height=600,
                    title=f"Publications from {org_name} - Research Areas vs. Citations")
                # return df, area_fig
                journal_fig = px.scatter(raw_df,
                            x="times_cited", y="journal.title",
                            marginal_x="histogram",
                            marginal_y="histogram",
                            height=600,
                            title=f"Publications from {org_name} - Journals vs. Citations")
                
                return df, area_fig, journal_fig
            else:
                return df



def get_geonames(**kwargs):
    """Get the geonames dataframe.

    Returns:
        pd.DataFrame: The dataframe of the results.
    """
    url = "https://raw.githubusercontent.com/giswqs/data/main/world/cities5000.csv"
    # columns = ['geonameid', 'name', 'asciiname', 'alternatenames', 'latitude', 'longitude', 'feature_class', 'feature_code', 'country_code',
    #            'cc2', 'admin1_code', 'admin2_code', 'admin3_code', 'admin4_code', 'population', 'elevation', 'dem', 'timezone', 'modification_date']
    df = pd.read_csv(url, sep="\t", encoding="utf-8")

    if "columns" in kwargs and isinstance(kwargs["columns"], list):
        df = df[kwargs["columns"]]
    else:
        df = df[
            ["geonameid", "name", "country_code",
                "population", "latitude", "longitude"]
        ]

    return df


def geoname_latlon(id, df=None):
    """Get the latitude and longitude of a city based on a GeoNmae city id.

    Args:
        id (str): The GeoName city id.
        df (pd.DataFrame, optional): The geonames dataframe. Defaults to None.

    Returns:
        tuple: The latitude and longitude of the city.
    """
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
    """Get the locations of collaborators.

    Args:
        df (pd.DataFrame): The dataframe of collaborators, can be derived from _, df = dsl.researcher_annual_stats().

    Returns:
        pd.DataFrame: The dataframe of the results.
    """
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
    """Get a barplot of the annual stats.

    Args:
        df (pd.DataFrame): The dataframe of the results. Can be derived from df, _ = dsl.researcher_annual_stats().
        columns (list, optional): The columns to plot. Defaults to None.

    Returns:
        px.Bar: The barplot.
    """
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
    """Convert a json file to a dataframe.

    Args:
        json_data (json): The json data.
        transpose (bool, optional): If True, transpose the dataframe. Defaults to False.

    Returns:
        pd.DataFrame: The dataframe of the results.
    """
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
