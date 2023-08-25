# -*- coding: utf-8 -*-
# ***********************************************************************
# ******************  CANADIAN ASTRONOMY DATA CENTRE  *******************
# *************  CENTRE CANADIEN DE DONNÉES ASTRONOMIQUES  **************
#
#  (c) 2023.                            (c) 2023.
#  Government of Canada                 Gouvernement du Canada
#  National Research Council            Conseil national de recherches
#  Ottawa, Canada, K1A 0R6              Ottawa, Canada, K1A 0R6
#  All rights reserved                  Tous droits réservés
#
#  NRC disclaims any warranties,        Le CNRC dénie toute garantie
#  expressed, implied, or               énoncée, implicite ou légale,
#  statutory, of any kind with          de quelque nature que ce
#  respect to the software,             soit, concernant le logiciel,
#  including without limitation         y compris sans restriction
#  any warranty of merchantability      toute garantie de valeur
#  or fitness for a particular          marchande ou de pertinence
#  purpose. NRC shall not be            pour un usage particulier.
#  liable in any event for any          Le CNRC ne pourra en aucun cas
#  damages, whether direct or           être tenu responsable de tout
#  indirect, special or general,        dommage, direct ou indirect,
#  consequential or incidental,         particulier ou général,
#  arising from the use of the          accessoire ou fortuit, résultant
#  software.  Neither the name          de l'utilisation du logiciel. Ni
#  of the National Research             le nom du Conseil National de
#  Council of Canada nor the            Recherches du Canada ni les noms
#  names of its contributors may        de ses  participants ne peuvent
#  be used to endorse or promote        être utilisés pour approuver ou
#  products derived from this           promouvoir les produits dérivés
#  software without specific prior      de ce logiciel sans autorisation
#  written permission.                  préalable et particulière
#                                       par écrit.
#
#  This file is part of the             Ce fichier fait partie du projet
#  OpenCADC project.                    OpenCADC.
#
#  OpenCADC is free software:           OpenCADC est un logiciel libre ;
#  you can redistribute it and/or       vous pouvez le redistribuer ou le
#  modify it under the terms of         modifier suivant les termes de
#  the GNU Affero General Public        la “GNU Affero General Public
#  License as published by the          License” telle que publiée
#  Free Software Foundation,            par la Free Software Foundation
#  either version 3 of the              : soit la version 3 de cette
#  License, or (at your option)         licence, soit (à votre gré)
#  any later version.                   toute version ultérieure.
#
#  OpenCADC is distributed in the       OpenCADC est distribué
#  hope that it will be useful,         dans l’espoir qu’il vous
#  but WITHOUT ANY WARRANTY;            sera utile, mais SANS AUCUNE
#  without even the implied             GARANTIE : sans même la garantie
#  warranty of MERCHANTABILITY          implicite de COMMERCIALISABILITÉ
#  or FITNESS FOR A PARTICULAR          ni d’ADÉQUATION À UN OBJECTIF
#  PURPOSE.  See the GNU Affero         PARTICULIER. Consultez la Licence
#  General Public License for           Générale Publique GNU Affero
#  more details.                        pour plus de détails.
#
#  You should have received             Vous devriez avoir reçu une
#  a copy of the GNU Affero             copie de la Licence Générale
#  General Public License along         Publique GNU Affero avec
#  with OpenCADC.  If not, see          OpenCADC ; si ce n’est
#  <http://www.gnu.org/licenses/>.      pas le cas, consultez :
#                                       <http://www.gnu.org/licenses/>.
#
#  $Revision: 4 $
#
# ***********************************************************************
#

"""
This module implements the ObsBlueprint mapping, as well as the workflow 
entry point that executes the workflow.
"""

from os.path import basename

from caom2 import CalibrationLevel, DataProductType, ProductType, ReleaseType
from caom2pipe import caom_composable as cc
from caom2pipe import manage_composable as mc


__all__ = [
    'SpiceRACSMapping',
    'SpiceRACSName',
]


class SpiceRACSName(mc.StorageName):
    """Naming rules:
    - support mixed-case file name storage, and mixed-case obs id values
    - support uncompressed files in storage
    """

    SPICERACS_NAME_PATTERN = '*'

    def __init__(self, entry):
        super().__init__(file_name=basename(entry), source_names=[entry])

    def set_obs_id(self, **kwargs):
        self._obs_id = '_'.join(ii for ii in self._file_id.split('_')[:-1])
    
    def set_product_id(self, **kwargs):
        self._product_id = self._file_id.split('_')[-1]

    def is_valid(self):
        return True


class SpiceRACSMapping(cc.TelescopeMapping):
    def __init__(self, storage_name, headers, clients, observable, observation):
        super().__init__(storage_name, headers, clients, observable, observation)

    def accumulate_blueprint(self, bp):
        """Configure the telescope-specific ObsBlueprint at the CAOM model
        Observation level."""
        self._logger.debug('Begin accumulate_bp.')
        super().accumulate_blueprint(bp)
        bp.set('Observation.target.type', 'field')
        # JW - SPICE-RACS is public data
        release_date = '2023-01-01T11:11:11'
        bp.set('Observation.metaRelease', release_date)
        bp.set('Plane.dataRelease', release_date)
        bp.set('Plane.metaRelease', release_date)
        bp.set('Plane.calibrationLevel', CalibrationLevel.CALIBRATED)
        bp.set('Plane.dataProductType', DataProductType.CUBE)
        bp.set('Artifact.productType', ProductType.SCIENCE)
        bp.set('Artifact.releaseType', ReleaseType.DATA)

        bp.configure_position_axes((1, 2))
        bp.clear('Chunk.position.axis.function.cd11')
        bp.clear('Chunk.position.axis.function.cd22')
        bp.add_attribute('Chunk.position.axis.function.cd11', 'CDELT1')
        bp.set('Chunk.position.axis.function.cd12', 0.0)
        bp.set('Chunk.position.axis.function.cd21', 0.0)
        bp.add_attribute('Chunk.position.axis.function.cd22', 'CDELT2')


        self._logger.debug('Done accumulate_bp.')

    def update(self, file_info):
        """Called to fill multiple CAOM model elements and/or attributes (an n:n relationship between TDM attributes
         and CAOM attributes).
        """
        return super().update(file_info)
